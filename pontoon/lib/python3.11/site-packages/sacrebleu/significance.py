import os
import logging
import multiprocessing as mp
from typing import Sequence, Dict, Optional, Tuple, List, Union, Any, Mapping

import numpy as np

from .metrics.base import Metric, Score, Signature

IS_WINDOWS = os.name == 'nt'


sacrelogger = logging.getLogger('sacrebleu')


class Result:
    """A container to represent results from a particular statistical
    significance test.
    :param score: The floating point score for the system at hand.
    :param p_value: If exists, represents the p-value when the system at
    hand is compared to a baseline using a paired test.
    :param mean: When paired bootstrap test is applied, this represents
    the true mean score estimated from bootstrap resamples of the system.
    :param ci: When paired bootstrap test is applied, this represents
    the 95% confidence interval around the true mean score `sys_mean`.
    """
    def __init__(self, score: float, p_value: Optional[float] = None,
                 mean: Optional[float] = None, ci: Optional[float] = None):
        self.score = score
        self.p_value = p_value
        self.mean = mean
        self.ci = ci

    def __repr__(self):
        return ','.join([f'{k}={str(v)}' for k, v in self.__dict__.items()])


def estimate_ci(scores: np.ndarray) -> Tuple[float, float]:
    """Takes a list of scores and returns mean and 95% confidence
    interval around the mean.

    :param scores: A list of floating point scores.
    :return: A tuple of mean and the 95% CI.
    """
    # Sort the scores
    scores = np.sort(scores)
    n = len(scores)

    # Get CI bounds (95%, i.e. 1/40 from left)
    lower_idx = n // 40
    upper_idx = n - lower_idx - 1
    lower, upper = scores[lower_idx], scores[upper_idx]
    ci = 0.5 * (upper - lower)
    return (scores.mean(), ci)


def _bootstrap_resample(stats: List[List[Union[int, float]]],
                        metric: Metric, n_samples: int = 1000) -> Tuple[str, List[Score]]:
    """Performs bootstrap resampling for a single system to estimate
    a confidence interval around the true mean.
    :param stats: A list of statistics extracted from the system's hypotheses.
    :param metric: The `Metric` instance to be used for score computation.
    :n_samples: Number of bootstrap resamples to use.

    :return: A tuple of the seed choice as string and the list of `Score`
    instances for all bootstrap resamples.
    """

    # Set numpy RNG's seed
    # If  given -> Fix to the given value
    # If given but =='[Nn]one', don't fix the seed i.e. pull entropy from OS
    seed = os.environ.get('SACREBLEU_SEED', '12345')
    _seed = None if seed.lower() == 'none' else int(seed)
    rng = np.random.default_rng(_seed)

    # The indices that'll produce all bootstrap resamples at once
    idxs = rng.choice(len(stats), size=(n_samples, len(stats)), replace=True)

    # convert to numpy array. float32 is more efficient
    stats_np = np.array(stats, dtype='float32')

    # recompute scores for all resamples
    scores = [
        metric._compute_score_from_stats(_s.sum(0)) for _s in stats_np[idxs]]

    return str(seed).lower(), scores


def _compute_p_value(stats: np.ndarray, real_difference: float) -> float:
    """Computes the p-value given the sample statistics and the real statistic.
    :param stats: A numpy array with the sample statistics.
    :real_difference: The real statistic.
    :return: The p-value.
    """
    # Taken from: significance/StratifiedApproximateRandomizationTest.java
    # https://github.com/jhclark/multeval.git

    # "the != is important. if we want to score the same system against itself
    # having a zero difference should not be attributed to chance."

    c = np.sum(stats > real_difference).item()

    # "+1 applies here, though it only matters for small numbers of shufflings,
    # which we typically never do. it's necessary to ensure the probability of
    # falsely rejecting the null hypothesis is no greater than the rejection
    # level of the test (see william and morgan on significance tests)
    p = (c + 1) / (len(stats) + 1)

    return p


def _paired_ar_test(baseline_info: Dict[str, Tuple[np.ndarray, Result]],
                    sys_name: str,
                    hypotheses: Sequence[str],
                    references: Optional[Sequence[Sequence[str]]],
                    metrics: Dict[str, Metric],
                    n_samples: int = 10000,
                    n_ar_confidence: int = -1,
                    seed: Optional[int] = None) -> Tuple[str, Dict[str, Result]]:
    """Paired two-sided approximate randomization (AR) test for MT evaluation.

    :param baseline_info: A dictionary with `Metric` instances as the keys,
    that contains sufficient statistics and a `Result` instance for the baseline system.
    :param sys_name: The name of the system to be evaluated.
    :param hypotheses: A sequence of string hypotheses for the system.
    :param references: A sequence of reference documents with document being
    defined as a sequence of reference strings. If `None`, references
    will be used through each metric's internal cache.
    :param metrics: A dictionary of `Metric` instances that will be computed
    for each system.
    :param n_samples: The number of AR trials.
    :param n_ar_confidence: The number of bootstrap resamples to use for
    confidence estimation. A value of -1 disables confidence estimation.
    :param seed: The seed value for the RNG. If `None`, the RNG will not be
    fixed to a particular seed.

    :return: A tuple with first element being the system name and the second
    being a `Result` namedtuple.
    """
    # Seed the RNG
    rng = np.random.default_rng(seed)

    # Generate indices that'll select stats
    pos_sel = rng.integers(2, size=(n_samples, len(hypotheses)), dtype=bool)

    # Flip mask to obtain selectors for system hypotheses
    neg_sel = ~pos_sel

    if n_ar_confidence > 0:
        # Perform confidence estimation as well
        bs_idxs = rng.choice(
            len(hypotheses), size=(n_ar_confidence, len(hypotheses)), replace=True)

    results = {}

    for name, metric in metrics.items():
        # Use pre-computed match stats for the baseline
        bl_stats, bl_result = baseline_info[name]

        # Compute system's stats and score
        sacrelogger.info(f'Computing {name} for {sys_name!r} and extracting sufficient statistics')
        sys_stats = metric._extract_corpus_statistics(hypotheses, references)
        sys_score = metric._aggregate_and_compute(sys_stats)

        # original test statistic: absolute difference between baseline and the system
        diff = abs(bl_result.score - sys_score.score)

        sacrelogger.info(f' > Performing approximate randomization test (# trials: {n_samples})')
        # get shuffled pseudo systems
        shuf_a = pos_sel @ bl_stats + neg_sel @ sys_stats
        shuf_b = neg_sel @ bl_stats + pos_sel @ sys_stats

        # Aggregate trial stats and compute scores for each
        scores_a = np.array(
            [metric._aggregate_and_compute(x).score for x in shuf_a[:, None]])
        scores_b = np.array(
            [metric._aggregate_and_compute(x).score for x in shuf_b[:, None]])

        # Count the statistical difference and compute the p-value
        p = _compute_p_value(
            np.abs(np.array(scores_a) - np.array(scores_b)), diff)

        res = Result(sys_score.score, p)

        if n_ar_confidence > 0:
            sacrelogger.info(f' > Performing bootstrap resampling for confidence interval (# resamples: {n_ar_confidence})')
            sys_stats = np.array(sys_stats, dtype='float32')
            # recompute scores for all resamples
            sys_scores = np.array([
                metric._compute_score_from_stats(_s.sum(0)).score for _s in sys_stats[bs_idxs]
            ])
            res.mean, res.ci = estimate_ci(sys_scores)

        # Store the result
        results[name] = res

    return sys_name, results


def _paired_bs_test(baseline_info: Dict[str, Tuple[np.ndarray, Result]],
                    sys_name: str,
                    hypotheses: Sequence[str],
                    references: Optional[Sequence[Sequence[str]]],
                    metrics: Dict[str, Metric],
                    n_samples: int = 1000,
                    n_ar_confidence: int = -1,
                    seed: Optional[int] = None) -> Tuple[str, Dict[str, Result]]:
    """Paired bootstrap resampling test for MT evaluation. This function
    replicates the behavior of the Moses script called
    `bootstrap-hypothesis-difference-significance.pl`.

    :param baseline_info: A dictionary with `Metric` instances as the keys,
    that contains sufficient statistics and a `Result` instance for the baseline system.
    :param sys_name: The name of the system to be evaluated.
    :param hypotheses: A sequence of string hypotheses for the system.
    :param references: A sequence of reference documents with document being
    defined as a sequence of reference strings. If `None`, references
    will be used through each metric's internal cache.
    :param metrics: A dictionary of `Metric` instances that will be computed
    for each system.
    :param n_samples: The number of bootstrap resamples.
    :param n_ar_confidence: This parameter is not used for this function but
    is there for signature compatibility in the API.
    :param seed: The seed value for the RNG. If `None`, the RNG will not be
    fixed to a particular seed.

    :return: A tuple with first element being the system name and the second
    being a `Result` namedtuple.
    """
    # Seed the RNG
    rng = np.random.default_rng(seed)

    results = {}

    # It takes ~10ms to generated the indices
    idxs = rng.choice(
        len(hypotheses), size=(n_samples, len(hypotheses)), replace=True)

    for name, metric in metrics.items():
        # Use pre-computed match stats for the baseline
        bl_stats, bl_result = baseline_info[name]

        # Compute system's stats and score
        sacrelogger.info(f'Computing {name} for {sys_name!r} and extracting sufficient statistics')
        sys_stats = metric._extract_corpus_statistics(hypotheses, references)
        sys_score = metric._aggregate_and_compute(sys_stats)

        # Convert to numpy arrays for efficient indexing
        sys_stats = np.array(sys_stats, dtype='float32')
        bl_stats = np.array(bl_stats, dtype='float32')

        # original test statistic: absolute difference between baseline and the system
        diff = abs(bl_result.score - sys_score.score)

        sacrelogger.info(f' > Performing paired bootstrap resampling test (# resamples: {n_samples})')
        scores_bl = np.array(
            [metric._compute_score_from_stats(_s.sum(0)).score for _s in bl_stats[idxs]])
        scores_sys = np.array(
            [metric._compute_score_from_stats(_s.sum(0)).score for _s in sys_stats[idxs]])

        # Compute CI as well
        sys_mean, sys_ci = estimate_ci(scores_sys)

        # Compute the statistics
        sample_diffs = np.abs(scores_sys - scores_bl)
        stats = sample_diffs - sample_diffs.mean()

        # Count the statistical difference and compute the p-value
        p = _compute_p_value(stats, diff)

        results[name] = Result(sys_score.score, p, sys_mean, sys_ci)

    return sys_name, results


class PairedTest:
    """This is the manager class that will call the actual standalone implementation
    for approximate randomization or paired bootstrap resampling, based on the
    `test_type` argument.

    :param named_systems: A lisf of (system_name, system_hypotheses) tuples on
    which the test will be applied.
    :param metrics: A dictionary of `Metric` instances that will be computed
    for each system.
    :param references: A sequence of reference documents with document being
    defined as a sequence of reference strings. If `None`, already cached references
    will be used through each metric's internal cache.
    :param test_type: `ar` for approximate randomization, `bs` for paired bootstrap.
    :param n_samples: The number of AR trials (for `ar`) or bootstrap resamples (for `bs`).
    The defaults (10000 or 1000 respectively) will be used if 0 is passed.
    :param n_ar_confidence: If `approximate randomization` is selected, the number
    of bootstrap resamples to use for confidence estimation. A value of -1 disables
    confidence estimation. 0 will use the default of 1000.
    :param n_jobs: If 0, a worker process will be spawned for each system variant.
    If > 0, the number of workers will be set accordingly. The default of 1
    does not use multi-processing.
    """
    _DEFAULT_SAMPLES = {
        'ar': 10000,
        'bs': 1000,
    }

    def __init__(self, named_systems: List[Tuple[str, Sequence[str]]],
                 metrics: Mapping[str, Metric],
                 references: Optional[Sequence[Sequence[str]]],
                 test_type: str = 'ar',
                 n_samples: int = 0,
                 n_ar_confidence: int = -1,
                 n_jobs: int = 1):
        assert test_type in ('ar', 'bs'), f"Unknown test type {test_type!r}"
        self.test_type = test_type

        # Set method
        if self.test_type == 'ar':
            self._fn = _paired_ar_test
        elif self.test_type == 'bs':
            self._fn = _paired_bs_test

        # Set numpy RNG's seed
        # If  given -> Fix to the given value
        # If given but =='[Nn]one', don't fix the seed i.e. pull entropy from OS
        seed = os.environ.get('SACREBLEU_SEED', '12345')
        self._seed = None if seed.lower() == 'none' else int(seed)
        self.n_jobs = n_jobs
        self.references = references
        self.named_systems = named_systems

        # Set the defaults if requested
        self.n_ar_confidence = n_ar_confidence if n_ar_confidence != 0 else \
            self._DEFAULT_SAMPLES['bs']

        self.n_samples = n_samples if n_samples > 0 else \
            self._DEFAULT_SAMPLES[self.test_type]

        # Number of systems (excluding the baseline)
        self.n_systems = len(named_systems) - 1

        # Decide on number of workers
        if IS_WINDOWS:
            sacrelogger.warning('Parallel tests are not supported on Windows.')
            self.n_jobs = 1
        elif self.n_jobs == 0:
            # Decide automatically
            # Divide by two to ignore hyper-threading
            n_max_jobs = mp.cpu_count() // 2
            if n_max_jobs == 0:
                self.n_jobs = 1
            else:
                # Don't use more workers than the number of CPUs
                self.n_jobs = min(n_max_jobs, self.n_systems)

        self._signatures: Dict[str, Signature] = {}
        self._baseline_info: Dict[str, Tuple[Any, Result]] = {}

        ##################################################
        # Pre-compute and cache baseline system statistics
        ##################################################
        self.metrics = {}

        bl_name, bl_hyps = self.named_systems[0]

        for name, metric in metrics.items():
            sacrelogger.info(f'Pre-computing {name} statistics for {bl_name!r}')
            bl_stats = metric._extract_corpus_statistics(bl_hyps, self.references)
            bl_score = metric._aggregate_and_compute(bl_stats)

            # Compute CI for the baseline here once
            confidence_n = self.n_samples if self.test_type == 'bs' \
                else self.n_ar_confidence

            bl_mean, bl_ci = None, None
            if confidence_n > 0:
                _, bl_scores = _bootstrap_resample(bl_stats, metric, confidence_n)
                bl_mean, bl_ci = estimate_ci(np.array([x.score for x in bl_scores]))

            result = Result(bl_score.score, mean=bl_mean, ci=bl_ci)
            # Use updated name for the metric
            self._baseline_info[bl_score.name] = (bl_stats, result)
            self.metrics[bl_score.name] = metric

            # Update metric signature as well
            sig = metric.get_signature()
            sig.update('seed', str(self._seed).lower())

            # Num samples for bs, num trials for AR
            sig.update(self.test_type, self.n_samples)
            if self.n_ar_confidence > 0:
                # Bootstrap is used for AR CI as well
                sig.update('bs', self.n_ar_confidence)
            self._signatures[bl_score.name] = sig

    def __call__(self) -> Tuple[Dict[str, Signature], Dict[str, List[Union[str, Result]]]]:
        """Runs the paired test either on single or multiple worker processes."""
        tasks = []
        scores: Dict[str, List[Union[str, Result]]] = {}

        # Add the name column
        scores['System'] = [ns[0] for ns in self.named_systems]

        # Store baseline results as the first position
        for metric, (_, result) in self._baseline_info.items():
            scores[metric] = [result]

        # Prepare list of arguments for each comparison
        # Skip the baseline (pos: 0)
        for idx, (name, hyps) in enumerate(self.named_systems[1:]):
            seed = self._seed if self._seed else None

            tasks.append(
                (self._baseline_info, name, hyps, self.references,
                 self.metrics, self.n_samples, self.n_ar_confidence, seed))

        # Run the test(s)
        if self.n_jobs == 1:
            results = [self._fn(*args) for args in tasks]
        else:
            # NOTE: The overhead of worker creation is not negligible
            # but if you have many systems and TER enabled, this significantly
            # speeds up the test.
            # NOTE: This only works on Linux/Mac OS X but not Windows. Windows only
            # supports `spawn` backend which requires things to be called
            # from within __main__.
            sacrelogger.info(f'Launching {self.n_jobs} parallel workers.')
            with mp.get_context('fork').Pool(self.n_jobs) as pool:
                jobs = [pool.apply_async(self._fn, args) for args in tasks]

                # wait for completion
                results = [j.get() for j in jobs]

        # Keep the order deterministic
        for sys_name, sys_results in results:
            for metric, _result in sys_results.items():
                scores[metric].append(_result)

        return self._signatures, scores
