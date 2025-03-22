"""The implementation of the TER metric (Snover et al., 2006)."""

# Copyright 2020 Memsource
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import List, Dict, Sequence, Optional, Any

from ..tokenizers.tokenizer_ter import TercomTokenizer
from ..utils import sum_of_lists
from .base import Score, Signature, Metric
from .lib_ter import translation_edit_rate


class TERSignature(Signature):
    """A convenience class to represent the reproducibility signature for TER.

    :param args: key-value dictionary passed from the actual metric instance.
    """
    def __init__(self, args: dict):
        """`TERSignature` initializer."""
        super().__init__(args)
        self._abbr.update({
            'case': 'c',
            'tok': 't',
            'norm': 'nr',
            'punct': 'pn',
            'asian': 'as',
        })

        self.info.update({
            'case': 'mixed' if args['case_sensitive'] else 'lc',
            'tok': args['tokenizer_signature'],
            'norm': args['normalized'],
            'punct': not args['no_punct'],
            'asian': args['asian_support'],
        })


class TERScore(Score):
    """A convenience class to represent TER scores.

    :param score: The TER score.
    :param num_edits: The cumulative number of edits.
    :param ref_length: The cumulative average reference length.
    """
    def __init__(self, score: float, num_edits: float, ref_length: float):
        """`TERScore` initializer."""
        super().__init__('TER', score)
        self.num_edits = int(num_edits)
        self.ref_length = ref_length


class TER(Metric):
    """Translation edit rate (TER). A near-exact reimplementation of the Tercom
    algorithm, produces identical results on all "sane" outputs.

    Tercom original implementation: https://github.com/jhclark/tercom

    The beam edit distance algorithm uses a slightly different approach (we stay
    around the diagonal which is faster, at least in Python) so in some
    (extreme) corner cases, the output could differ.

    Caching in the edit distance is based partly on the PyTer package by Hiroyuki
    Tanaka (MIT license). (https://github.com/aflc/pyter)

    :param normalized: Enable character normalization. By default, normalizes a couple of things such as
        newlines being stripped, retrieving XML encoded characters, and fixing tokenization for punctuation. When
        'asian_support' is enabled, also normalizes specific Asian (CJK) character sequences, i.e.
        split them down to the character level.
    :param no_punct: Remove punctuation. Can be used in conjunction with 'asian_support' to also remove typical
        punctuation markers in Asian languages (CJK).
    :param asian_support: Enable special treatment of Asian characters. This option only has an effect when
        'normalized' and/or 'no_punct' is enabled. If 'normalized' is also enabled, then Asian (CJK)
        characters are split down to the character level. If 'no_punct' is enabled alongside 'asian_support',
        specific unicode ranges for CJK and full-width punctuations are also removed.
    :param case_sensitive: If `True`, does not lowercase sentences.
    :param references: A sequence of reference documents with document being
        defined as a sequence of reference strings. If given, the reference info
        will be pre-computed and cached for faster re-computation across many systems.
    """

    _SIGNATURE_TYPE = TERSignature

    def __init__(self, normalized: bool = False,
                 no_punct: bool = False,
                 asian_support: bool = False,
                 case_sensitive: bool = False,
                 references: Optional[Sequence[Sequence[str]]] = None):
        """`TER` initializer."""
        super().__init__()

        self.no_punct = no_punct
        self.normalized = normalized
        self.asian_support = asian_support
        self.case_sensitive = case_sensitive

        self.tokenizer = TercomTokenizer(
            normalized=self.normalized,
            no_punct=self.no_punct,
            asian_support=self.asian_support,
            case_sensitive=self.case_sensitive,
        )
        self.tokenizer_signature = self.tokenizer.signature()

        if references is not None:
            self._ref_cache = self._cache_references(references)

    def _preprocess_segment(self, sent: str) -> str:
        """Given a sentence, apply tokenization if enabled.

        :param sent: The input sentence string.
        :return: The pre-processed output string.
        """
        return self.tokenizer(sent.rstrip())

    def _compute_score_from_stats(self, stats: List[float]) -> TERScore:
        """Computes the final score from already aggregated statistics.

        :param stats: A list or numpy array of segment-level statistics.
        :return: A `TERScore` object.
        """
        total_edits, sum_ref_lengths = stats[0], stats[1]

        if sum_ref_lengths > 0:
            score = total_edits / sum_ref_lengths
        elif total_edits > 0:
            score = 1.0  # empty reference(s) and non-empty hypothesis
        else:
            score = 0.0  # both reference(s) and hypothesis are empty

        return TERScore(100 * score, total_edits, sum_ref_lengths)

    def _aggregate_and_compute(self, stats: List[List[float]]) -> TERScore:
        """Computes the final TER score given the pre-computed corpus statistics.

        :param stats: A list of segment-level statistics
        :return: A `TERScore` instance.
        """
        return self._compute_score_from_stats(sum_of_lists(stats))

    def _compute_segment_statistics(
            self, hypothesis: str, ref_kwargs: Dict) -> List[float]:
        """Given a (pre-processed) hypothesis sentence and already computed
        reference words, returns the segment statistics required to compute
        the full TER score.

        :param hypothesis: Hypothesis sentence.
        :param ref_kwargs: A dictionary with `ref_words` key which is a list
        where each sublist contains reference words.
        :return: A two-element list that contains the 'minimum number of edits'
        and 'the average reference length'.
        """

        ref_lengths = 0
        best_num_edits = int(1e16)

        words_hyp = hypothesis.split()

        # Iterate the references
        ref_words = ref_kwargs['ref_words']
        for words_ref in ref_words:
            num_edits, ref_len = translation_edit_rate(words_hyp, words_ref)
            ref_lengths += ref_len
            if num_edits < best_num_edits:
                best_num_edits = num_edits

        avg_ref_len = ref_lengths / len(ref_words)
        return [best_num_edits, avg_ref_len]

    def _extract_reference_info(self, refs: Sequence[str]) -> Dict[str, Any]:
        """Given a list of reference segments, applies pre-processing & tokenization
        and returns list of tokens for each reference.

        :param refs: A sequence of strings.
        :return: A dictionary that will be passed to `_compute_segment_statistics()`
        through keyword arguments.
        """
        ref_words = []

        for ref in refs:
            ref_words.append(self._preprocess_segment(ref).split())

        return {'ref_words': ref_words}
