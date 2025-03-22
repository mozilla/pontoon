"""The implementation of the BLEU metric (Papineni et al., 2002)."""

import math
import logging
from importlib import import_module
from typing import List, Sequence, Optional, Dict, Any

from ..utils import my_log, sum_of_lists

from .base import Score, Signature, Metric
from .helpers import extract_all_word_ngrams

sacrelogger = logging.getLogger('sacrebleu')

# The default for the maximum n-gram order when computing precisions
MAX_NGRAM_ORDER = 4

_TOKENIZERS = {
    'none': 'tokenizer_none.NoneTokenizer',
    'zh': 'tokenizer_zh.TokenizerZh',
    '13a': 'tokenizer_13a.Tokenizer13a',
    'intl': 'tokenizer_intl.TokenizerV14International',
    'char': 'tokenizer_char.TokenizerChar',
    'ja-mecab': 'tokenizer_ja_mecab.TokenizerJaMecab',
    'ko-mecab': 'tokenizer_ko_mecab.TokenizerKoMecab',
    'spm': 'tokenizer_spm.TokenizerSPM',
    'flores101': 'tokenizer_spm.Flores101Tokenizer',
    'flores200': 'tokenizer_spm.Flores200Tokenizer',
}


def _get_tokenizer(name: str):
    """Dynamically import tokenizer as importing all is slow."""
    module_name, class_name = _TOKENIZERS[name].rsplit('.', 1)
    return getattr(
        import_module(f'.tokenizers.{module_name}', 'sacrebleu'),
        class_name)


class BLEUSignature(Signature):
    """A convenience class to represent the reproducibility signature for BLEU.

    :param args: key-value dictionary passed from the actual metric instance.
    """
    def __init__(self, args: dict):
        """`BLEUSignature` initializer."""
        super().__init__(args)

        self._abbr.update({
            'case': 'c',
            'eff': 'e',
            'tok': 'tok',
            'smooth': 's',
        })

        # Construct a combined string for smoothing method and value
        smooth_str = args['smooth_method']
        smooth_def = BLEU.SMOOTH_DEFAULTS[smooth_str]

        # If the method requires a parameter, add it within brackets
        if smooth_def is not None:
            # the following can be None if the user wants to use the default
            smooth_val = args['smooth_value']

            if smooth_val is None:
                smooth_val = smooth_def

            smooth_str += f'[{smooth_val:.2f}]'

        self.info.update({
            'case': 'lc' if args['lowercase'] else 'mixed',
            'eff': 'yes' if args['effective_order'] else 'no',
            'tok': args['tokenizer_signature'],
            'smooth': smooth_str,
        })


class BLEUScore(Score):
    """A convenience class to represent BLEU scores.

    :param score: The BLEU score.
    :param counts: List of counts of correct ngrams, 1 <= n <= max_ngram_order
    :param totals: List of counts of total ngrams, 1 <= n <= max_ngram_order
    :param precisions: List of precisions, 1 <= n <= max_ngram_order
    :param bp: The brevity penalty.
    :param sys_len: The cumulative system length.
    :param ref_len: The cumulative reference length.
    """
    def __init__(self, score: float, counts: List[int], totals: List[int],
                 precisions: List[float], bp: float,
                 sys_len: int, ref_len: int):
        """`BLEUScore` initializer."""
        super().__init__('BLEU', score)
        self.bp = bp
        self.counts = counts
        self.totals = totals
        self.sys_len = sys_len
        self.ref_len = ref_len
        self.precisions = precisions

        self.prec_str = "/".join([f"{p:.1f}" for p in self.precisions])
        self.ratio = self.sys_len / self.ref_len if self.ref_len else 0

        # The verbose part of BLEU
        self._verbose = f"{self.prec_str} (BP = {self.bp:.3f} "
        self._verbose += f"ratio = {self.ratio:.3f} hyp_len = {self.sys_len:d} "
        self._verbose += f"ref_len = {self.ref_len:d})"


class BLEU(Metric):
    """Computes the BLEU metric given hypotheses and references.

    :param lowercase: If True, lowercased BLEU is computed.
    :param force: Ignore data that looks already tokenized.
    :param tokenize: The tokenizer to use. If None, defaults to language-specific tokenizers with '13a' as the fallback default.
    :param smooth_method: The smoothing method to use ('floor', 'add-k', 'exp' or 'none').
    :param smooth_value: The smoothing value for `floor` and `add-k` methods. `None` falls back to default value.
    :param max_ngram_order: If given, it overrides the maximum n-gram order (default: 4) when computing precisions.
    :param effective_order: If `True`, stop including n-gram orders for which precision is 0. This should be
        `True`, if sentence-level BLEU will be computed.
    :param trg_lang: An optional language code to raise potential tokenizer warnings.
    :param references: A sequence of reference documents with document being
    defined as a sequence of reference strings. If given, the reference n-grams
    and lengths will be pre-computed and cached for faster BLEU computation
    across many systems.
    """

    SMOOTH_DEFAULTS: Dict[str, Optional[float]] = {
        # The defaults for `floor` and `add-k` are obtained from the following paper
        # A Systematic Comparison of Smoothing Techniques for Sentence-Level BLEU
        # Boxing Chen and Colin Cherry
        # http://aclweb.org/anthology/W14-3346
        'none': None,   # No value is required
        'floor': 0.1,
        'add-k': 1,
        'exp': None,    # No value is required
    }

    TOKENIZERS = _TOKENIZERS.keys()

    # mteval-v13a.pl tokenizer unless Chinese or Japanese is provided
    TOKENIZER_DEFAULT = '13a'

    # Some language specific mappings to use if `trg_lang` is given
    # and the tokenizer is not explicitly specified
    _TOKENIZER_MAP = {
        'zh': 'zh',
        'ja': 'ja-mecab',
        'ko': 'ko-mecab',
    }

    _SIGNATURE_TYPE = BLEUSignature

    def __init__(self, lowercase: bool = False,
                 force: bool = False,
                 tokenize: Optional[str] = None,
                 smooth_method: str = 'exp',
                 smooth_value: Optional[float] = None,
                 max_ngram_order: int = MAX_NGRAM_ORDER,
                 effective_order: bool = False,
                 trg_lang: str = '',
                 references: Optional[Sequence[Sequence[str]]] = None):
        """`BLEU` initializer."""
        super().__init__()

        self._force = force
        self.trg_lang = trg_lang
        self.lowercase = lowercase
        self.smooth_value = smooth_value
        self.smooth_method = smooth_method
        self.max_ngram_order = max_ngram_order
        self.effective_order = effective_order

        # Sanity check
        assert self.smooth_method in self.SMOOTH_DEFAULTS.keys(), \
            "Unknown smooth_method {self.smooth_method!r}"

        # If the tokenizer wasn't specified, choose it according to the
        # following logic. We use 'v13a' except for ZH and JA. Note that
        # this logic can only be applied when sacrebleu knows the target
        # language, which is only the case for builtin datasets.
        if tokenize is None:
            best_tokenizer = self.TOKENIZER_DEFAULT

            # Set `zh` or `ja-mecab` or `ko-mecab` if target language is provided
            if self.trg_lang in self._TOKENIZER_MAP:
                best_tokenizer = self._TOKENIZER_MAP[self.trg_lang]
        else:
            best_tokenizer = tokenize
            if self.trg_lang == 'zh' and best_tokenizer != 'zh':
                sacrelogger.warning(
                    "Consider using the 'zh' or 'spm' tokenizer for Chinese.")
            if self.trg_lang == 'ja' and best_tokenizer != 'ja-mecab':
                sacrelogger.warning(
                    "Consider using the 'ja-mecab' or 'spm' tokenizer for Japanese.")
            if self.trg_lang == 'ko' and best_tokenizer != 'ko-mecab':
                sacrelogger.warning(
                    "Consider using the 'ko-mecab' or 'spm' tokenizer for Korean.")

        # Create the tokenizer
        self.tokenizer = _get_tokenizer(best_tokenizer)()

        # Build the signature
        self.tokenizer_signature = self.tokenizer.signature()

        if references is not None:
            # Pre-compute reference ngrams and lengths
            self._ref_cache = self._cache_references(references)

    @staticmethod
    def compute_bleu(correct: List[int],
                     total: List[int],
                     sys_len: int,
                     ref_len: int,
                     smooth_method: str = 'none',
                     smooth_value=None,
                     effective_order: bool = False,
                     max_ngram_order: int = MAX_NGRAM_ORDER) -> BLEUScore:
        """Computes BLEU score from its sufficient statistics with smoothing.

        Smoothing methods (citing "A Systematic Comparison of Smoothing Techniques for Sentence-Level BLEU",
        Boxing Chen and Colin Cherry, WMT 2014: http://aclweb.org/anthology/W14-3346)

        - none: No smoothing.
        - floor: Method 1 (requires small positive value (0.1 in the paper) to be set)
        - add-k: Method 2 (Generalizing Lin and Och, 2004)
        - exp: Method 3 (NIST smoothing method i.e. in use with mteval-v13a.pl)

        :param correct: List of counts of correct ngrams, 1 <= n <= max_ngram_order
        :param total: List of counts of total ngrams, 1 <= n <= max_ngram_order
        :param sys_len: The cumulative system length
        :param ref_len: The cumulative reference length
        :param smooth_method: The smoothing method to use ('floor', 'add-k', 'exp' or 'none')
        :param smooth_value: The smoothing value for `floor` and `add-k` methods. `None` falls back to default value.
        :param effective_order: If `True`, stop including n-gram orders for which precision is 0. This should be
            `True`, if sentence-level BLEU will be computed.
        :param max_ngram_order: If given, it overrides the maximum n-gram order (default: 4) when computing precisions.
        :return: A `BLEUScore` instance.
        """
        assert smooth_method in BLEU.SMOOTH_DEFAULTS.keys(), \
            "Unknown smooth_method {smooth_method!r}"

        # Fetch the default value for floor and add-k
        if smooth_value is None:
            smooth_value = BLEU.SMOOTH_DEFAULTS[smooth_method]

        # Compute brevity penalty
        if sys_len < ref_len:
            bp = math.exp(1 - ref_len / sys_len) if sys_len > 0 else 0.0
        else:
            bp = 1.0

        # n-gram precisions
        precisions = [0.0 for x in range(max_ngram_order)]

        # Early stop if there are no matches (#141)
        if not any(correct):
            return BLEUScore(0.0, correct, total, precisions, bp, sys_len, ref_len)

        smooth_mteval = 1.
        eff_order = max_ngram_order
        for n in range(1, len(precisions) + 1):
            if smooth_method == 'add-k' and n > 1:
                correct[n - 1] += smooth_value
                total[n - 1] += smooth_value

            if total[n - 1] == 0:
                break

            # If the system guesses no i-grams, 1 <= i <= max_ngram_order,
            # the BLEU score is 0 (technically undefined). This is a problem for sentence
            # level BLEU or a corpus of short sentences, where systems will get
            # no credit if sentence lengths fall under the max_ngram_order threshold.
            # This fix scales max_ngram_order to the observed maximum order.
            # It is only available through the API and off by default
            if effective_order:
                eff_order = n

            if correct[n - 1] == 0:
                if smooth_method == 'exp':
                    smooth_mteval *= 2
                    precisions[n - 1] = 100. / (smooth_mteval * total[n - 1])
                elif smooth_method == 'floor':
                    precisions[n - 1] = 100. * smooth_value / total[n - 1]
            else:
                precisions[n - 1] = 100. * correct[n - 1] / total[n - 1]

        # Compute BLEU score
        score = bp * math.exp(
            sum([my_log(p) for p in precisions[:eff_order]]) / eff_order)

        return BLEUScore(score, correct, total, precisions, bp, sys_len, ref_len)

    def _preprocess_segment(self, sent: str) -> str:
        """Given a sentence, lowercases (optionally) and tokenizes it
        :param sent: The input sentence string.
        :return: The pre-processed output string.
        """
        if self.lowercase:
            sent = sent.lower()
        return self.tokenizer(sent.rstrip())

    def _compute_score_from_stats(self, stats: List[int]) -> BLEUScore:
        """Computes the final score from already aggregated statistics.

        :param stats: A list or numpy array of segment-level statistics.
        :return: A `BLEUScore` object.
        """
        return self.compute_bleu(
            correct=stats[2: 2 + self.max_ngram_order],
            total=stats[2 + self.max_ngram_order:],
            sys_len=int(stats[0]), ref_len=int(stats[1]),
            smooth_method=self.smooth_method, smooth_value=self.smooth_value,
            effective_order=self.effective_order,
            max_ngram_order=self.max_ngram_order
        )

    def _aggregate_and_compute(self, stats: List[List[int]]) -> BLEUScore:
        """Computes the final BLEU score given the pre-computed corpus statistics.

        :param stats: A list of segment-level statistics
        :return: A `BLEUScore` instance.
        """
        return self._compute_score_from_stats(sum_of_lists(stats))

    def _get_closest_ref_len(self, hyp_len: int, ref_lens: List[int]) -> int:
        """Given a hypothesis length and a list of reference lengths, returns
        the closest reference length to be used by BLEU.

        :param hyp_len: The hypothesis length.
        :param ref_lens: A list of reference lengths.
        :return: The closest reference length.
        """
        closest_diff, closest_len = -1, -1

        for ref_len in ref_lens:
            diff = abs(hyp_len - ref_len)
            if closest_diff == -1 or diff < closest_diff:
                closest_diff = diff
                closest_len = ref_len
            elif diff == closest_diff and ref_len < closest_len:
                closest_len = ref_len

        return closest_len

    def _extract_reference_info(self, refs: Sequence[str]) -> Dict[str, Any]:
        """Given a list of reference segments, extract the n-grams and reference lengths.
        The latter will be useful when comparing hypothesis and reference lengths for BLEU.

        :param refs: A sequence of strings.
        :return: A dictionary that will be passed to `_compute_segment_statistics()`
        through keyword arguments.
        """
        ngrams = None
        ref_lens = []

        for ref in refs:
            # extract n-grams for this ref
            this_ngrams, ref_len = extract_all_word_ngrams(ref, 1, self.max_ngram_order)
            ref_lens.append(ref_len)

            if ngrams is None:
                # Set it directly for first set of refs
                ngrams = this_ngrams
            else:
                # Merge counts across multiple references
                # The below loop is faster than `ngrams |= this_ngrams`
                for ngram, count in this_ngrams.items():
                    ngrams[ngram] = max(ngrams[ngram], count)

        return {'ref_ngrams': ngrams, 'ref_lens': ref_lens}

    def _compute_segment_statistics(self, hypothesis: str,
                                    ref_kwargs: Dict) -> List[int]:
        """Given a (pre-processed) hypothesis sentence and already computed
        reference n-grams & lengths, returns the best match statistics across the
        references.

        :param hypothesis: Hypothesis sentence.
        :param ref_kwargs: A dictionary with `refs_ngrams`and `ref_lens` keys
        that denote the counter containing all n-gram counts and reference lengths,
        respectively.
        :return: A list of integers with match statistics.
        """

        ref_ngrams, ref_lens = ref_kwargs['ref_ngrams'], ref_kwargs['ref_lens']

        # Extract n-grams for the hypothesis
        hyp_ngrams, hyp_len = extract_all_word_ngrams(
            hypothesis, 1, self.max_ngram_order)

        ref_len = self._get_closest_ref_len(hyp_len, ref_lens)

        # Count the stats
        # Although counter has its internal & and | operators, this is faster
        correct = [0 for i in range(self.max_ngram_order)]
        total = correct[:]
        for hyp_ngram, hyp_count in hyp_ngrams.items():
            # n-gram order
            n = len(hyp_ngram) - 1
            # count hypothesis n-grams
            total[n] += hyp_count
            # count matched n-grams
            if hyp_ngram in ref_ngrams:
                correct[n] += min(hyp_count, ref_ngrams[hyp_ngram])

        # Return a flattened list for efficient computation
        return [hyp_len, ref_len] + correct + total

    def sentence_score(self, hypothesis: str, references: Sequence[str]) -> BLEUScore:
        """Compute the metric for a single sentence against a single (or multiple) reference(s).

        :param hypothesis: A single hypothesis string.
        :param references: A sequence of reference strings.
        :return: a `BLEUScore` object.
        """
        if not self.effective_order:
            sacrelogger.warning(
                'It is recommended to enable `effective_order` for sentence-level BLEU.')
        return super().sentence_score(hypothesis, references)
