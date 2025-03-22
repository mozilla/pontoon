"""The implementation of chrF (Popović 2015) and chrF++ (Popović 2017) metrics."""

from typing import List, Sequence, Optional, Dict
from collections import Counter

from ..utils import sum_of_lists
from .base import Score, Signature, Metric
from .helpers import extract_all_char_ngrams, extract_word_ngrams


class CHRFSignature(Signature):
    """A convenience class to represent the reproducibility signature for chrF.

    :param args: key-value dictionary passed from the actual metric instance.
    """
    def __init__(self, args: dict):
        """`CHRFSignature` initializer."""
        super().__init__(args)
        self._abbr.update({
            'case': 'c',
            'eff': 'e',
            'nc': 'nc',
            'nw': 'nw',
            'space': 's',
        })

        self.info.update({
            'case': 'lc' if args['lowercase'] else 'mixed',
            'eff': 'yes' if not args['eps_smoothing'] else 'no',
            'nc': args['char_order'],
            'nw': args['word_order'],
            'space': 'yes' if args['whitespace'] else 'no',
        })


class CHRFScore(Score):
    """A convenience class to represent chrF scores.

    :param score: The chrF (chrF++) score.
    :param char_order: The character n-gram order.
    :param word_order: The word n-gram order. If equals to 2, the metric is referred to as chrF++.
    :param beta: Determine the importance of recall w.r.t precision.
    """
    def __init__(self, score: float, char_order: int, word_order: int, beta: int):
        """`CHRFScore` initializer."""
        self.beta = beta
        self.char_order = char_order
        self.word_order = word_order

        # Add + signs to denote chrF+ variant
        name = f'chrF{self.beta}' + '+' * self.word_order

        super().__init__(name, score)


class CHRF(Metric):
    """Computes the chrF(++) metric given hypotheses and references.

    :param char_order: Character n-gram order.
    :param word_order: Word n-gram order. If equals to 2, the metric is referred to as chrF++.
    :param beta: Determine the importance of recall w.r.t precision.
    :param lowercase: Enable case-insensitivity.
    :param whitespace: If `True`, include whitespaces when extracting character n-grams.
    :param eps_smoothing: If `True`, applies epsilon smoothing similar
    to reference chrF++.py, NLTK and Moses implementations. Otherwise,
    it takes into account effective match order similar to sacreBLEU < 2.0.0.
    :param references: A sequence of reference documents with document being
    defined as a sequence of reference strings. If given, the reference n-grams
    will be pre-computed and cached for faster re-computation across many systems.
    """

    # Maximum character n-gram order to take into account
    CHAR_ORDER = 6

    # chrF+ additionally takes into account some of the word n-grams
    WORD_ORDER = 0

    # Defaults to 2 (per http://www.aclweb.org/anthology/W16-2341)
    BETA = 2

    # Cache string.punctuation for chrF+' punctuation stripper
    _PUNCTS = set('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')

    _SIGNATURE_TYPE = CHRFSignature

    def __init__(self, char_order: int = CHAR_ORDER,
                 word_order: int = WORD_ORDER,
                 beta: int = BETA,
                 lowercase: bool = False,
                 whitespace: bool = False,
                 eps_smoothing: bool = False,
                 references: Optional[Sequence[Sequence[str]]] = None):
        """`CHRF` initializer."""
        super().__init__()

        self.beta = beta
        self.char_order = char_order
        self.word_order = word_order
        self.order = self.char_order + self.word_order
        self.lowercase = lowercase
        self.whitespace = whitespace
        self.eps_smoothing = eps_smoothing

        if references is not None:
            # Pre-compute reference ngrams
            self._ref_cache = self._cache_references(references)

    @staticmethod
    def _get_match_statistics(hyp_ngrams: Counter, ref_ngrams: Counter) -> List[int]:
        """Computes the match statistics between hypothesis and reference n-grams.

        :param hyp_ngrams: A `Counter` holding hypothesis n-grams.
        :param ref_ngrams: A `Counter` holding reference n-grams.
        :return: A list of three numbers denoting hypothesis n-gram count,
            reference n-gram count and the intersection count.
        """
        # Counter's internal intersection is not that fast, count manually
        match_count, hyp_count = 0, 0
        for ng, count in hyp_ngrams.items():
            hyp_count += count
            if ng in ref_ngrams:
                match_count += min(count, ref_ngrams[ng])

        return [
            # Don't count hits if no reference exists for that n-gram
            hyp_count if ref_ngrams else 0,
            sum(ref_ngrams.values()),
            match_count,
        ]

    def _remove_punctuation(self, sent: str) -> List[str]:
        """Separates out punctuations from beginning and end of words for chrF.
        Adapted from https://github.com/m-popovic/chrF

        :param sent: A string.
        :return: A list of words.
        """
        tokenized = []
        for w in sent.split():
            if len(w) == 1:
                tokenized.append(w)
            else:
                # NOTE: This splits '(hi)' to '(hi' and ')' (issue #124)
                if w[-1] in self._PUNCTS:
                    tokenized += [w[:-1], w[-1]]
                elif w[0] in self._PUNCTS:
                    tokenized += [w[0], w[1:]]
                else:
                    tokenized.append(w)
        return tokenized

    def _preprocess_segment(self, sent: str) -> str:
        """Given a sentence, apply optional lowercasing.

        :param sent: The input sentence string.
        :return: The pre-processed output string.
        """
        return sent.lower() if self.lowercase else sent

    def _compute_f_score(self, statistics: List[int]) -> float:
        """Compute the chrF score given the n-gram match statistics.

        :param statistics: A flattened list of 3 * (`char_order` + `word_order`)
            elements giving the [hyp, ref, match] counts for each order.
        :return: The final f_beta score between [0, 100].
        """
        eps = 1e-16
        score = 0.0
        effective_order = 0
        factor = self.beta ** 2
        avg_prec, avg_rec = 0.0, 0.0

        for i in range(self.order):
            n_hyp, n_ref, n_match = statistics[3 * i: 3 * i + 3]

            # chrF++.py style EPS smoothing (also used by Moses and NLTK)
            prec = n_match / n_hyp if n_hyp > 0 else eps
            rec = n_match / n_ref if n_ref > 0 else eps

            denom = factor * prec + rec
            score += ((1 + factor) * prec * rec / denom) if denom > 0 else eps

            # sacreBLEU <2.0.0 style effective order smoothing
            if n_hyp > 0 and n_ref > 0:
                avg_prec += prec
                avg_rec += rec
                effective_order += 1

        if self.eps_smoothing:
            return 100 * score / self.order

        if effective_order == 0:
            avg_prec = avg_rec = 0.0
        else:
            avg_prec /= effective_order
            avg_rec /= effective_order

        if avg_prec + avg_rec:
            score = (1 + factor) * avg_prec * avg_rec
            score /= ((factor * avg_prec) + avg_rec)
            return 100 * score
        else:
            return 0.0

    def _compute_score_from_stats(self, stats: List[int]) -> CHRFScore:
        """Computes the final score from already aggregated statistics.

        :param stats: A list or numpy array of segment-level statistics.
        :return: A `CHRFScore` object.
        """
        return CHRFScore(
            self._compute_f_score(stats), self.char_order,
            self.word_order, self.beta)

    def _aggregate_and_compute(self, stats: List[List[int]]) -> CHRFScore:
        """Computes the final score given the pre-computed corpus statistics.

        :param stats: A list of segment-level statistics
        :return: A `CHRFScore` object.
        """
        return self._compute_score_from_stats(sum_of_lists(stats))

    def _extract_reference_info(self, refs: Sequence[str]) -> Dict[str, List[List[Counter]]]:
        """Given a list of reference segments, extract the character and word n-grams.

        :param refs: A sequence of reference segments.
        :return: A list where each element contains n-grams per reference segment.
        """
        ngrams = []

        for ref in refs:
            # extract character n-grams
            stats = extract_all_char_ngrams(ref, self.char_order, self.whitespace)

            # Check chrF+ mode
            if self.word_order > 0:
                ref_words = self._remove_punctuation(ref)

                for n in range(self.word_order):
                    stats.append(extract_word_ngrams(ref_words, n + 1))

            ngrams.append(stats)

        return {'ref_ngrams': ngrams}

    def _compute_segment_statistics(
            self, hypothesis: str, ref_kwargs: Dict) -> List[int]:
        """Given a (pre-processed) hypothesis sentence and already computed
        reference n-grams, returns the best match statistics across the
        references.

        :param hypothesis: Hypothesis sentence.
        :param ref_kwargs: A dictionary with key `ref_ngrams` which is a list
        where each sublist contains n-gram counters for a particular reference sentence.
        :return: A list of integers where each triplet denotes [hyp, ref, match]
        statistics.
        """
        best_stats = []
        best_f_score = -1.0

        # extract character n-grams
        all_hyp_ngrams = extract_all_char_ngrams(
            hypothesis, self.char_order, self.whitespace)

        # Check chrF+ mode to see if we'll add word n-grams as well
        if self.word_order > 0:
            # Primitive tokenization: separate out punctuations
            hwords = self._remove_punctuation(hypothesis)
            _range = range(1, self.word_order + 1)
            all_hyp_ngrams.extend([extract_word_ngrams(hwords, n) for n in _range])

        # Iterate over multiple references, pick the one with best F score
        for _ref_ngrams in ref_kwargs['ref_ngrams']:
            stats = []
            # Traverse all orders
            for h, r in zip(all_hyp_ngrams, _ref_ngrams):
                stats.extend(self._get_match_statistics(h, r))
            f_score = self._compute_f_score(stats)

            if f_score > best_f_score:
                best_f_score = f_score
                best_stats = stats

        return best_stats
