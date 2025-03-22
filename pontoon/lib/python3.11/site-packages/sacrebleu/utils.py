import itertools
import json
import os
import re
import sys
import gzip
import math
import hashlib
import logging
import portalocker
from collections import defaultdict
from typing import List, Optional, Sequence, Dict
from argparse import Namespace

from tabulate import tabulate
import colorama


# Where to store downloaded test sets.
# Define the environment variable $SACREBLEU, or use the default of ~/.sacrebleu.
#
# Querying for a HOME environment variable can result in None (e.g., on Windows)
# in which case the os.path.join() throws a TypeError. Using expanduser() is
# a safe way to get the user's home folder.
USERHOME = os.path.expanduser("~")
SACREBLEU_DIR = os.environ.get('SACREBLEU', os.path.join(USERHOME, '.sacrebleu'))

sacrelogger = logging.getLogger('sacrebleu')


class Color:
    ENABLE_COLORS = True

    @staticmethod
    def format(msg: str, color: str) -> str:
        """Returns a colored version of the given message string.

        :param msg: The string to Color.format.
        :param color: The color specifier i.e. 'red', 'blue', 'green', etc.
        :return: A colored version of the string if the output is a terminal.
        """
        if not Color.ENABLE_COLORS:
            return msg
        _ansi_str = getattr(colorama.Fore, color.upper(), None)
        if _ansi_str:
            return f'{_ansi_str}{msg}{colorama.Style.RESET_ALL}'

        return msg


def _format_score_lines(scores: dict,
                        width: int = 2,
                        multiline: bool = True) -> Dict[str, List[str]]:
    """Formats the scores prior to tabulating them."""
    new_scores = {'System': scores.pop('System')}
    p_val_break_char = '\n' if multiline else ' '
    is_bootstrap = False

    def _color_p_value(p: float):
        msg = f'(p = {p:.4f})'
        if p > 0.05:
            return Color.format(msg, 'red')
        return msg + '*'

    for metric, vals in scores.items():
        new_vals = []

        for result in vals:
            if not isinstance(result, str):
                # Format result instances
                _str = f'{result.score:.{width}f}'
                if result.mean is not None:
                    is_bootstrap = True
                    _str += f' ({result.mean:.{width}f} ± {result.ci:.{width}f})'
                if result.p_value is not None:
                    _str += p_val_break_char + _color_p_value(result.p_value)
            else:
                # Already formatted in non paired-test mode
                _str = result

            new_vals.append(_str)

        if is_bootstrap:
            # Change titles
            metric += ' (μ ± 95% CI)'

        new_scores[metric] = new_vals

    return new_scores


def print_results_table(results: dict, signatures: dict, args: Namespace):
    """Prints out a nicely formatted table for multi-system evaluation mode."""

    if args.format == 'json':
        proper_json = []
        dict_keys = list(results.keys())
        for i in range(len(results['System'])):
            value = {}
            value['system'] = results['System'][i]
            # parse metrics
            for j in range(1, len(dict_keys)):
                if isinstance(results[dict_keys[j]][i], str):
                    value[dict_keys[j]] = results[dict_keys[j]][i]
                else:
                    # Values inside object as dict
                    value[dict_keys[j]] = results[dict_keys[j]][i].__dict__
            proper_json.append(value)

        print(json.dumps(proper_json, indent=4))
        return

    tablefmt = args.format
    if tablefmt in ('text'):
        tablefmt = 'fancy_grid'
    elif tablefmt == 'latex':
        # Use booktabs
        tablefmt = 'latex_booktabs'

    # If paired testing has been given, this'll format the score lines
    results = _format_score_lines(
        results, args.width, multiline=tablefmt == 'fancy_grid')

    new_dict = {}

    # Color the column names and the baseline system name and scores
    has_baseline = False
    baseline_name = ''
    for name in results.keys():
        val = results[name]
        if val[0].startswith('Baseline:') or has_baseline:
            if val[0].startswith('Baseline:'):
                baseline_name = val[0]
            has_baseline = True
            val[0] = Color.format(val[0], 'yellow')
        new_dict[Color.format(name, 'cyan')] = results[name]

    # Finally tabulate
    table = tabulate(
        new_dict, headers='keys', tablefmt=tablefmt,
        colalign=('right', ),
        stralign='center',
        numalign='center',
        floatfmt=f'.{args.width}f')

    print(table)
    print()

    is_paired = args.paired_bs or args.paired_ar

    if is_paired:
        test_type = 'bootstrap resampling' if args.paired_bs else 'approximate randomization'
        n_samples_or_trials = args.paired_bs_n if args.paired_bs else args.paired_ar_n
        test_sample_type = 'resampling trials' if args.paired_bs else 'trials'
        msg = f'Paired {test_type} test with {n_samples_or_trials} {test_sample_type}'

        bline = Color.format('baseline', 'yellow')
        bline_name = Color.format(baseline_name, 'yellow')
        null_hyp = Color.format('Null hypothesis', 'green')
        pval_color = Color.format('highlighted in red', 'red')

        # Print fancy header
        print('-' * len(msg) + '\n' + msg + '\n' + '-' * len(msg))
        print(f' - Each system is pairwise compared to {bline_name}.')
        if args.paired_bs:
            print('   Actual system score / bootstrap estimated true mean / 95% CI are provided for each metric.')
        else:
            print('   Actual system score is provided for each metric.')
        print()
        print(f' - {null_hyp}: the system and the {bline} translations are essentially')
        print(f'   generated by the same underlying process. For a given system and the {bline},')
        print('   the p-value is roughly the probability of the absolute score difference (delta)')
        print(f'   or higher occurring due to chance, under the assumption that the {null_hyp.lower()} is correct.')
        print()
        print(f' - Assuming a significance threshold of 0.05, the {null_hyp.lower()} can be rejected')
        print('   for p-values < 0.05 (marked with "*"). This means that the delta is unlikely to be attributed')
        print(f'   to chance, hence the system is significantly "different" than the {bline}.')
        print(f'   Otherwise, the p-values are {pval_color}.')
        print()
        print(f' - NOTE: Significance does not tell whether a system is "better" than the {bline} but rather')
        print('   emphasizes the "difference" of the systems in terms of the replicability of the delta.')
        print()

    print('-----------------')
    print('Metric signatures')
    print('-----------------')
    for name, sig in signatures.items():
        print(f' - {name:<10} {sig}')


def print_single_results(results: List[str], args: Namespace):
    """Re-process metric strings to align them nicely."""
    if args.format == 'json':
        if len(results) > 1:
            proper_json = '[\n' + ',\n'.join(results) + '\n]'
            print(proper_json)
        else:
            print(results[0])
        return

    # Color confidence strings for emphasis
    if 'μ' in results[0]:
        color_re = re.compile(r'(\(μ = [0-9\.]+ ± [0-9\.]+\))')
        for idx in range(len(results)):
            results[idx] = color_re.sub(
                lambda m: Color.format(m.group(), 'cyan'), results[idx])

    if len(results) == 1:
        # Just one system, nothing to align.
        print(results[0])
        return

    # Align by '=' character
    lens = []
    for line in results:
        # If not score_only, split lines from '=' for re-alignment
        try:
            lens.append(line.index('=') - 1)
        except ValueError:
            print(line)

    if len(lens) > 0:
        w = max(lens)
        for (_len, line) in zip(lens, results):
            left, right = line[:_len], line[_len:]
            print(f'{left:>{w}}{right}')


def sanity_check_lengths(system: Sequence[str],
                         refs: Sequence[Sequence[str]],
                         test_set: Optional[str] = None):
    n_hyps = len(system)
    if any(len(ref_stream) != n_hyps for ref_stream in refs):
        sacrelogger.error("System and reference streams have different lengths.")
        if test_set:
            sacrelogger.error("This could be an issue with your system output "
                              "or with sacreBLEU's reference database if -t is given.")
            sacrelogger.error("For the latter, try cleaning out the cache by typing:\n")
            sacrelogger.error(f"  rm -r {SACREBLEU_DIR}/{test_set}\n")
            sacrelogger.error("The test sets will be re-downloaded the next time you run sacreBLEU.")
        sys.exit(1)


def smart_open(file, mode='rt', encoding='utf-8'):
    """Convenience function for reading compressed or plain text files.
    :param file: The file to read.
    :param mode: The file mode (read, write).
    :param encoding: The file encoding.
    """
    if file.endswith('.gz'):
        return gzip.open(file, mode=mode, encoding=encoding, newline="\n")
    return open(file, mode=mode, encoding=encoding, newline="\n")


def my_log(num: float) -> float:
    """
    Floors the log function

    :param num: the number
    :return: log(num) floored to a very low number
    """

    if num == 0.0:
        return -9999999999
    return math.log(num)


def sum_of_lists(lists):
    """Aggregates list of numeric lists by summing."""
    if len(lists) == 1:
        return lists[0]

    # Preserve datatype
    size = len(lists[0])
    init_val = type(lists[0][0])(0.0)
    total = [init_val] * size
    for ll in lists:
        for i in range(size):
            total[i] += ll[i]
    return total


def args_to_dict(args, prefix: str, strip_prefix: bool = False):
    """Filters argparse's `Namespace` into dictionary with arguments
    beginning with the given prefix."""
    prefix += '_'
    d = {}
    for k, v in args.__dict__.items():
        if k.startswith(prefix):
            k = k.replace(prefix, '') if strip_prefix else k
            d[k] = v
    return d


def print_test_set(test_set, langpair, requested_fields, origlang=None, subset=None):
    """Prints to STDOUT the specified side of the specified test set.

    :param test_set: the test set to print
    :param langpair: the language pair
    :param requested_fields: the fields to print
    :param origlang: print only sentences with a given original language (2-char ISO639-1 code), "non-" prefix means negation
    :param subset: print only sentences whose document annotation matches a given regex
    """
    if test_set not in DATASETS:
        raise Exception(f"No such test set {test_set}")

    fieldnames = DATASETS[test_set].fieldnames(langpair)
    all_files = DATASETS[test_set].get_files(langpair)

    if "all" in requested_fields and len(requested_fields) != 1:
        sacrelogger.error("Cannot use --echo all with other fields")
        sys.exit(1)
    elif "all" in requested_fields:
        requested_fields = fieldnames

    # backwards compatibility: allow "ref" even if not present (choose first)
    if "ref" in requested_fields and "ref" not in fieldnames:
        replacement_ref = min([f for f in fieldnames if f.startswith("ref")])
        requested_fields = [f if f != "ref" else replacement_ref for f in requested_fields]

    files = []
    for field in requested_fields:
        if field not in fieldnames:
            sacrelogger.error(f"No such field {field} in test set {test_set} for language pair {langpair}.")
            sacrelogger.error(f"available fields for {test_set}/{langpair}: {', '.join(fieldnames)}")
            if "ref" not in fieldnames:
                subref = min([f for f in fieldnames if f.startswith("ref")])
                sacrelogger.error(f"'ref' also allowed for backwards compatibility (will return {subref})")
            sys.exit(1)
        index = fieldnames.index(field)
        files.append(all_files[index])

    streams = [smart_open(file) for file in files]
    streams = filter_subset(streams, test_set, langpair, origlang, subset)
    for lines in zip(*streams):
        print('\t'.join(map(lambda x: x.rstrip(), lines)))


def get_source_file(test_set: str, langpair: str) -> str:
    """
    Returns the source file for a given testset/langpair.
    Downloads it first if it is not already local.

    :param test_set: The test set (e.g., "wmt19")
    :param langpair: The language pair (e.g., "de-en")
    :return: the path to the requested source file
    """
    if test_set not in DATASETS:
        raise Exception(f"No such test set {test_set}")

    return DATASETS[test_set].get_source_file(langpair)


def get_reference_files(test_set: str, langpair: str) -> List[str]:
    """
    Returns a list of one or more reference file paths for the given testset/langpair.
    Downloads the references first if they are not already local.

    :param test_set: The test set (e.g., "wmt19")
    :param langpair: The language pair (e.g., "de-en")
    :return: a list of one or more reference file paths
    """
    if test_set not in DATASETS:
        raise Exception(f"No such test set {test_set}")
    return DATASETS[test_set].get_reference_files(langpair)


def get_files(test_set, langpair) -> List[str]:
    """
    Returns the path of the source file and all reference files for
    the provided test set / language pair.
    Downloads the references first if they are not already local.

    :param test_set: The test set (e.g., "wmt19")
    :param langpair: The language pair (e.g., "de-en")
    :return: a list of the source file and all reference files
    """

    if test_set not in DATASETS:
        raise Exception(f"No such test set {test_set}")
    return DATASETS[test_set].get_files(langpair)


def extract_tarball(filepath, destdir):
    sacrelogger.info(f'Extracting {filepath} to {destdir}')
    if filepath.endswith('.tar.gz') or filepath.endswith('.tgz'):
        import tarfile
        with tarfile.open(filepath) as tar:
            tar.extractall(path=destdir)
    elif filepath.endswith('.zip'):
        import zipfile
        with zipfile.ZipFile(filepath, 'r') as zipfile:
            zipfile.extractall(path=destdir)


def get_md5sum(dest_path):
    # Check md5sum
    md5 = hashlib.md5()
    with open(dest_path, 'rb') as infile:
        for line in infile:
            md5.update(line)
    return md5.hexdigest()


def download_file(source_path, dest_path, extract_to=None, expected_md5=None):
    """Downloading utility.

    Downloads the specified test to the system location specified by the SACREBLEU environment variable.

    :param source_path: the remote uri to download
    :param dest_path: where to save the file
    :param extract_to: for tarballs, where to extract to
    :param expected_md5: the MD5 sum
    :return: the set of processed file names
    """
    import urllib.request
    import ssl

    outdir = os.path.dirname(dest_path)
    os.makedirs(outdir, exist_ok=True)

    # Make sure to open in mode "a"
    lockfile = f"{dest_path}.lock"
    with portalocker.Lock(lockfile, timeout=60):

        if not os.path.exists(dest_path) or os.path.getsize(dest_path) == 0:
            sacrelogger.info(f"Downloading {source_path} to {dest_path}")

            try:
                with urllib.request.urlopen(source_path) as f, open(dest_path, 'wb') as out:
                    out.write(f.read())
            except ssl.SSLError:
                sacrelogger.error('An SSL error was encountered in downloading the files. If you\'re on a Mac, '
                                    'you may need to run the "Install Certificates.command" file located in the '
                                    '"Python 3" folder, often found under /Applications')
                sys.exit(1)

            if expected_md5 is not None:
                cur_md5 = get_md5sum(dest_path)
                if cur_md5 != expected_md5:
                    sacrelogger.error(f'Fatal: MD5 sum of downloaded file was incorrect (got {cur_md5}, expected {expected_md5}).')
                    sacrelogger.error(f'Please manually delete {dest_path!r} and rerun the command.')
                    sacrelogger.error('If the problem persists, the tarball may have changed, in which case, please contact the SacreBLEU maintainer.')
                    sys.exit(1)

            # Extract the tarball
            if extract_to is not None:
                extract_tarball(dest_path, extract_to)


def download_test_set(test_set, langpair=None):
    """Downloads the specified test to the system location specified by the SACREBLEU environment variable.

    :param test_set: the test set to download
    :param langpair: the language pair (needed for some datasets)
    :return: the set of processed file names
    """
    if test_set not in DATASETS:
        raise Exception(f"No such test set {test_set}")
    dataset = DATASETS[test_set]
    file_paths = dataset.get_files(langpair)
    return file_paths


def get_langpairs_for_testset(testset: str) -> List[str]:
    """Return a list of language pairs for a given test set."""
    if testset not in DATASETS:
        return []
    return list(DATASETS[testset].langpairs.keys())


def get_available_testsets() -> List[str]:
    """Return a list of available test sets."""
    return sorted(DATASETS.keys(), reverse=True)

def get_available_testsets_for_langpair(langpair: str) -> List[str]:
    """Return a list of available test sets for a given language pair"""
    parts = langpair.split('-')
    srclang = parts[0]
    trglang = parts[1]

    testsets = []
    for dataset in DATASETS.values():
        if f'{srclang}-{trglang}' in dataset.langpairs \
                or f'{trglang}-{srclang}' in dataset.langpairs:
            testsets.append(dataset.name)

    return testsets


def get_available_origlangs(test_sets, langpair) -> List[str]:
    """Return a list of origlang values according to the raw XML/SGM files."""
    if test_sets is None:
        return []

    origlangs = set()
    for test_set in test_sets.split(','):
        dataset = DATASETS[test_set]
        rawfile = os.path.join(SACREBLEU_DIR, test_set, 'raw', dataset.langpairs[langpair][0])
        from .dataset.wmt_xml import WMTXMLDataset
        if isinstance(dataset, WMTXMLDataset):
            for origlang in dataset._unwrap_wmt21_or_later(rawfile)['origlang']:
                origlangs.add(origlang)
        if rawfile.endswith('.sgm'):
            with smart_open(rawfile) as fin:
                for line in fin:
                    if line.startswith('<doc '):
                        doc_origlang = re.sub(r'.* origlang="([^"]+)".*\n', '\\1', line)
                        origlangs.add(doc_origlang)
    return sorted(list(origlangs))


def get_available_subsets(test_sets, langpair) -> List[str]:
    """Return a list of domain values according to the raw XML files and domain/country values from the SGM files."""
    if test_sets is None:
        return []

    subsets = set()
    for test_set in test_sets.split(','):
        dataset = DATASETS[test_set]
        from .dataset.wmt_xml import WMTXMLDataset
        if isinstance(dataset, WMTXMLDataset):
            rawfile = os.path.join(SACREBLEU_DIR, test_set, 'raw', dataset.langpairs[langpair][0])
            fields = dataset._unwrap_wmt21_or_later(rawfile)
            if 'domain' in fields:
                subsets |= set(fields['domain'])
        elif test_set in SUBSETS:
            subsets |= set("country:" + v.split("-")[0] for v in SUBSETS[test_set].values())
            subsets |= set(v.split("-")[1] for v in SUBSETS[test_set].values())
    return sorted(list(subsets))

def filter_subset(systems, test_sets, langpair, origlang, subset=None):
    """Filter sentences with a given origlang (or subset) according to the raw SGM files."""
    if origlang is None and subset is None:
        return systems
    if test_sets is None or langpair is None:
        raise ValueError('Filtering for --origlang or --subset needs a test (-t) and a language pair (-l).')

    if subset is not None and subset.startswith('country:'):
        subset = subset[8:]

    re_origlang = re.compile(r'.* origlang="([^"]+)".*\n')
    re_id = re.compile(r'.* docid="([^"]+)".*\n')

    indices_to_keep = []
    for test_set in test_sets.split(','):
        dataset = DATASETS[test_set]
        rawfile = os.path.join(SACREBLEU_DIR, test_set, 'raw', dataset.langpairs[langpair][0])
        from .dataset.wmt_xml import WMTXMLDataset
        if isinstance(dataset, WMTXMLDataset):
            fields = dataset._unwrap_wmt21_or_later(rawfile)
            domains = fields['domain'] if 'domain' in fields else itertools.repeat(None)
            for doc_origlang, doc_domain in zip(fields['origlang'], domains):
                if origlang is None:
                    include_doc = True
                else:
                    if origlang.startswith('non-'):
                        include_doc = doc_origlang != origlang[4:]
                    else:
                        include_doc = doc_origlang == origlang
                if subset is not None and (doc_domain is None or not re.search(subset, doc_domain)):
                    include_doc = False
                indices_to_keep.append(include_doc)
        elif rawfile.endswith('.sgm'):
            doc_to_tags = {}
            if subset is not None:
                if test_set not in SUBSETS:
                    raise Exception('No subset annotation available for test set ' + test_set)
                doc_to_tags = SUBSETS[test_set]
            with smart_open(rawfile) as fin:
                include_doc = False
                for line in fin:
                    if line.startswith('<doc '):
                        if origlang is None:
                            include_doc = True
                        else:
                            doc_origlang = re_origlang.sub(r'\1', line)
                            if origlang.startswith('non-'):
                                include_doc = doc_origlang != origlang[4:]
                            else:
                                include_doc = doc_origlang == origlang

                        if subset is not None:
                            doc_id = re_id.sub(r'\1', line)
                            if not re.search(subset, doc_to_tags.get(doc_id, '')):
                                include_doc = False
                    if line.startswith('<seg '):
                        indices_to_keep.append(include_doc)
        else:
            raise Exception(f'--origlang and --subset supports only WMT *.xml and *.sgm files, not {rawfile!r}')
    return [[sentence for sentence, keep in zip(sys, indices_to_keep) if keep] for sys in systems]


def print_subset_results(metrics, full_system, full_refs, args):
    w = args.width
    origlangs = args.origlang if args.origlang else \
        get_available_origlangs(args.test_set, args.langpair)

    if len(origlangs) == 0:
        print('No subset information found. Consider using --origlang argument.')
        return

    results = defaultdict(list)

    for origlang in origlangs:
        subsets = [None]
        if args.subset is not None:
            subsets += [args.subset]
        else:
            subsets += get_available_subsets(args.test_set, args.langpair)

        for subset in subsets:
            system, *refs = filter_subset(
                [full_system, *full_refs], args.test_set, args.langpair, origlang, subset)

            if len(system) == 0:
                continue

            key = f'origlang={origlang}'
            if subset is None:
                key += ' domain=ALL'
            elif subset.startswith('country:'):
                key += f' country={subset[8:]}'
            else:
                key += f' domain={subset}'

            for metric in metrics.values():
                score = metric.corpus_score(system, refs)
                results[key].append((len(system), score))

    max_left_width = max([len(k) for k in results.keys()]) + 1
    max_metric_width = max([len(val[1].name) for val in list(results.values())[0]])
    for key, scores in results.items():
        key = Color.format(f'{key:<{max_left_width}}', 'yellow')
        for n_system, score in scores:
            print(f'{key}: sentences={n_system:<6} {score.name:<{max_metric_width}} = {score.score:.{w}f}')

# import at the end to avoid circular import
from .dataset import DATASETS, SUBSETS  # noqa: E402
