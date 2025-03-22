"""The base `Score`, `Metric` and `Signature` classes to derive from.

`Metric` is an abstract class that enforces the implementation of a set
of abstract methods. This way, a correctly implemented metric will work
seamlessly with the rest of the codebase.
"""

import json
import logging
import statistics
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional, Sequence

from ..version import __version__

sacrelogger = logging.getLogger("sacrebleu")


class Score:
    """A base score class to derive from.

    :param name: The name of the underlying metric.
    :param score: A floating point number for the final metric.
    """

    def __init__(self, name: str, score: float):
        """`Score` initializer."""
        self.name = name
        self.score = score

        # Statistical test related fields
        self._mean = -1.0
        self._ci = -1.0

        # More info can be added right after the score
        self._verbose = ""

    def format(
        self,
        width: int = 2,
        score_only: bool = False,
        signature: str = "",
        is_json: bool = False,
    ) -> str:
        """Returns a pretty representation of the score.
        :param width: Floating point decimal precision width.
        :param score_only: If `True`, and the format is not `json`,
        returns a single score string.
        :param signature: A string representation of the given `Signature`
        instance.
        :param is_json: If `True`, will output the score in JSON string.
        :return: A plain or JSON-formatted string representation.
        """
        d = {
            "name": self.name,
            "score": float(f"{self.score:.{width}f}"),
            "signature": signature,
        }

        sc = f"{self.score:.{width}f}"

        if self._mean > 0:
            confidence_mean = f"{self._mean:.{width}f}"
            confidence_var = f"{self._ci:.{width}f}"
            confidence_str = f"μ = {confidence_mean} ± {confidence_var}"

            sc += f" ({confidence_str})"
            if is_json:
                d["confidence_mean"] = float(confidence_mean)
                d["confidence_var"] = float(confidence_var)
                d["confidence"] = confidence_str

        # Construct full score line
        full_score = f"{self.name}|{signature}" if signature else self.name
        full_score = f"{full_score} = {sc}"
        if self._verbose:
            full_score += f" {self._verbose}"
            d["verbose_score"] = self._verbose

        if score_only:
            return sc

        if is_json:
            for param in signature.split("|"):
                key, value = param.split(":")
                d[key] = value
            return json.dumps(d, indent=1, ensure_ascii=False)

        return full_score

    def estimate_ci(self, scores: List["Score"]):
        """Takes a list of scores and stores mean, stdev and 95% confidence
        interval around the mean.

        :param scores: A list of `Score` objects obtained from bootstrap
        resampling for example.
        """
        # Sort the scores
        raw_scores = sorted([x.score for x in scores])
        n = len(raw_scores)

        # Get CI bounds (95%, i.e. 1/40 from left)
        lower_idx = n // 40
        upper_idx = n - lower_idx - 1
        lower, upper = raw_scores[lower_idx], raw_scores[upper_idx]
        self._ci = 0.5 * (upper - lower)
        self._mean = statistics.mean(raw_scores)

    def __repr__(self):
        """Returns a human readable score string."""
        return self.format()


class Signature:
    """A convenience class to represent sacreBLEU reproducibility signatures.

    :param args: key-value dictionary passed from the actual metric instance.
    """

    def __init__(self, args: dict):
        """`Signature` initializer."""
        # Global items that are shared across all metrics
        self._abbr = {
            "version": "v",
            "nrefs": "#",
            "test": "t",
            "lang": "l",
            "subset": "S",
            "origlang": "o",
            "bs": "bs",  # Bootstrap resampling trials
            "ar": "ar",  # Approximate randomization trials
            "seed": "rs",  # RNG's seed
        }

        if "num_refs" not in args:
            raise ValueError(
                "Number of references unknown, please evaluate the metric first."
            )

        num_refs = args["num_refs"]
        if num_refs == -1:
            # Detect variable number of refs
            num_refs = "var"

        # Global items that are shared across all metrics
        # None's will be ignored
        self.info = {
            "version": __version__,
            "nrefs": num_refs,
            "bs": args.get("n_bootstrap", None),
            "ar": None,
            "seed": args.get("seed", None),
            "test": args.get("test_set", None),
            "lang": args.get("langpair", None),
            "origlang": args.get("origlang", None),
            "subset": args.get("subset", None),
        }

    def format(self, short: bool = False) -> str:
        """Returns a string representation of the signature.

        :param short: If True, shortened signature is produced.
        :return: A string representation of the signature.
        """
        pairs = []
        keys = list(self.info.keys())
        # keep version always at end
        keys.remove("version")
        for name in keys + ["version"]:
            value = self.info[name]
            if value is not None:
                if isinstance(value, bool):
                    # Replace True/False with yes/no
                    value = "yes" if value else "no"
                final_name = self._abbr[name] if short else name
                pairs.append(f"{final_name}:{value}")

        return "|".join(pairs)

    def update(self, key: str, value: Any):
        """Add a new item or update an existing one.

        :param key: The key to use in the dictionary.
        :param value: The associated value for the `key`.
        """
        self.info[key] = value

    def __str__(self):
        """Returns a human-readable signature string."""
        return self.format()

    def __repr__(self):
        """Returns a human-readable signature string."""
        return self.format()


class Metric(metaclass=ABCMeta):
    """A base class for all metrics that ensures the implementation of some
    methods. Much of the common functionality is moved to this base class
    from other metrics."""

    # Each metric should define its Signature class' name here
    _SIGNATURE_TYPE = Signature

    def __init__(self):
        """`Metric` initializer."""
        # The pre-computed reference cache
        self._ref_cache = None

        # only useful for BLEU tokenized warnings. Set to True so that
        # warnings are not issued for other metrics.
        self._force = True

        # Will be used by the signature when bootstrap resampling
        self.n_bootstrap = None
        self.seed = None

    def _check_sentence_score_args(self, hyp: str, refs: Sequence[str]):
        """Performs sanity checks on `sentence_score` method's arguments.

        :param hyp: A single hypothesis string.
        :param refs: A sequence of reference strings.
        """
        prefix = self.__class__.__name__
        err_msg = None

        if not isinstance(hyp, str):
            err_msg = "The argument `hyp` should be a string."
        elif isinstance(refs, str) or not isinstance(refs, Sequence):
            err_msg = "The argument `refs` should be a sequence of strings."
        elif not isinstance(refs[0], str) and refs[0] is not None:
            err_msg = "Each element of `refs` should be a string."

        if err_msg:
            raise TypeError(f"{prefix}: {err_msg}")

    def _check_corpus_score_args(
        self, hyps: Sequence[str], refs: Optional[Sequence[Sequence[str]]]
    ):
        """Performs sanity checks on `corpus_score` method's arguments.

        :param hypses: A sequence of hypothesis strings.
        :param refs: A sequence of reference documents with document being
        defined as a sequence of reference strings. If `None`, cached references
        will be used.
        """

        prefix = self.__class__.__name__
        err_msg = None

        if not isinstance(hyps, Sequence):
            err_msg = "`hyps` should be a sequence of strings."
        elif not isinstance(hyps[0], str):
            err_msg = "Each element of `hyps` should be a string."
        elif any(line is None for line in hyps):
            err_msg = "Undefined line in hypotheses stream!"

        if refs is not None:
            if not isinstance(refs, Sequence):
                err_msg = "`refs` should be a sequence of sequence of strings."
            elif not isinstance(refs[0], Sequence):
                err_msg = "Each element of `refs` should be a sequence of strings."
            elif not isinstance(refs[0][0], str) and refs[0][0] is not None:
                err_msg = "`refs` should be a sequence of sequence of strings."

        if err_msg:
            raise TypeError(f"{prefix}: {err_msg}")

    @abstractmethod
    def _aggregate_and_compute(self, stats: List[List[Any]]) -> Any:
        """Computes the final score given the pre-computed match statistics.

        :param stats: A list of segment-level statistics.
        :return: A `Score` instance.
        """
        pass

    @abstractmethod
    def _compute_score_from_stats(self, stats: List[Any]) -> Any:
        """Computes the final score from already aggregated statistics.

        :param stats: A list or numpy array of segment-level statistics.
        :return: A `Score` object.
        """
        pass

    @abstractmethod
    def _preprocess_segment(self, sent: str) -> str:
        """A wrapper around the metric's tokenization and pre-processing logic.
        This should be implemented for reference caching to work correctly.

        :param sent: The input sentence.
        :return: The pre-processed output sentence.
        """
        pass

    @abstractmethod
    def _extract_reference_info(self, refs: Sequence[str]) -> Dict[str, Any]:
        """Given a list of reference segments, extract the required
        information (such as n-grams for BLEU and chrF). This should be implemented
        for the generic `_cache_references()` to work across all metrics.

        :param refs: A sequence of strings.
        """
        pass

    @abstractmethod
    def _compute_segment_statistics(
        self, hypothesis: str, ref_kwargs: Dict
    ) -> List[Any]:
        """Given a (pre-processed) hypothesis sentence and already computed
        reference info, returns the best match statistics across the
        references. The return type is usually a List of ints or floats.

        :param hypothesis: A pre-processed hypothesis sentence.
        :param ref_kwargs: A dictionary with reference-related information
        within. This is formulated as a dictionary as different metrics may
        require different information regarding a reference segment.
        """
        pass

    def _cache_references(self, references: Sequence[Sequence[str]]) -> List[Any]:
        """Given the full set of document references, extract segment n-grams
        (or other necessary information) for caching purposes.

        :param references: A sequence of reference documents with document being
        defined as a sequence of reference strings. A particular reference
        segment can be '' or `None` to allow the use of variable number
        of references per segment.
        :return: A list where each element is a tuple of segment n-grams and
        reference lengths, as returned by `_extract_reference_info()`.
        """
        ref_cache = []

        # Decide on final number of refs here as well
        num_refs = set()

        for refs in zip(*references):
            # Remove undefined references
            lines = [x for x in refs if x is not None]

            # Keep track of reference counts to allow variable reference
            # info in the signature
            num_refs.add(len(lines))

            lines = [self._preprocess_segment(x) for x in lines]

            # Get n-grams
            ref_cache.append(self._extract_reference_info(lines))

        if len(num_refs) == 1:
            self.num_refs = list(num_refs)[0]
        else:
            # A variable number of refs exist
            self.num_refs = -1

        return ref_cache

    def _extract_corpus_statistics(
        self, hypotheses: Sequence[str], references: Optional[Sequence[Sequence[str]]]
    ) -> Any:
        """Reads the corpus and returns sentence-level match statistics for
        faster re-computations esp. during statistical tests.

        :param hypotheses: A sequence of hypothesis strings.
        :param references: A sequence of reference documents with document being
        defined as a sequence of reference strings. If `None`, cached references
        will be used.
        :return: A list where each sublist corresponds to segment statistics.
        """
        # Pre-compute references
        # Don't store the cache as the user is explicitly passing refs
        if references:
            ref_cache = self._cache_references(references)
        elif self._ref_cache:
            ref_cache = self._ref_cache
        else:
            raise RuntimeError("No references provided and the cache is empty.")

        stats = []
        tok_count = 0

        for hyp, ref_kwargs in zip(hypotheses, ref_cache):
            # Check for already-tokenized input problem (only for BLEU)
            if not self._force and hyp.endswith(" ."):
                tok_count += 1

            hyp = self._preprocess_segment(hyp)

            # Collect stats
            stats.append(self._compute_segment_statistics(hyp, ref_kwargs))

        if tok_count >= 100:
            sacrelogger.warning("That's 100 lines that end in a tokenized period ('.')")
            sacrelogger.warning(
                "It looks like you forgot to detokenize your test data, which may hurt your score."
            )
            sacrelogger.warning(
                "If you insist your data is detokenized, or don't care, you can suppress this message with the `force` parameter."
            )

        return stats

    def sentence_score(self, hypothesis: str, references: Sequence[str]) -> Any:
        """Compute the metric for a single sentence against a single (or multiple) reference(s).

        :param hypothesis: A single hypothesis string.
        :param references: A sequence of reference strings.
        :return: A `Score` object.
        """
        self._check_sentence_score_args(hypothesis, references)

        stats = self._extract_corpus_statistics(
            [hypothesis], [[refs] for refs in references]
        )
        return self._aggregate_and_compute(stats)

    def corpus_score(
        self,
        hypotheses: Sequence[str],
        references: Optional[Sequence[Sequence[str]]],
        n_bootstrap: int = 1,
    ) -> Any:
        """Compute the metric for a corpus against a single (or multiple) reference(s).

        :param hypotheses: A sequence of hypothesis strings.
        :param references: A sequence of reference documents with document being
        defined as a sequence of reference strings. If `None`, cached references
        will be used.
        :param n_bootstrap: If > 1, provides 95% confidence interval around true mean
        using bootstrap resampling with `n_bootstrap` samples.
        :return: A `Score` object.
        """
        self._check_corpus_score_args(hypotheses, references)

        # Collect corpus stats
        stats = self._extract_corpus_statistics(hypotheses, references)

        # Compute the actual system score
        actual_score = self._aggregate_and_compute(stats)

        if n_bootstrap > 1:
            # Compute bootstrap estimate as well
            # Delayed import is to escape from numpy import if bootstrap
            # is not requested.
            from ..significance import _bootstrap_resample

            self.n_bootstrap = n_bootstrap
            self.seed, bs_scores = _bootstrap_resample(stats, self, n_bootstrap)
            actual_score.estimate_ci(bs_scores)

        return actual_score

    def get_signature(self) -> Signature:
        """Creates and returns the signature for the metric. The creation
        of signatures is delayed as the number of references is resolved
        only at the point of reference caching."""
        return self._SIGNATURE_TYPE(self.__dict__)
