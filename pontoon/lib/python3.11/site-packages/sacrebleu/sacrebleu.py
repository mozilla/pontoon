#!/usr/bin/env python3

# Copyright 2017--2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""
SacreBLEU provides hassle-free computation of shareable, comparable, and reproducible BLEU scores.
Inspired by Rico Sennrich's `multi-bleu-detok.perl`, it produces the official WMT scores but works with plain text.
It also knows all the standard test sets and handles downloading, processing, and tokenization for you.

See the [README.md] file for more information.
"""

import io
import os
import sys
import logging
import pathlib
import argparse
from collections import defaultdict


# Allows calling the script as a standalone utility
# See: https://github.com/mjpost/sacrebleu/issues/86
if __package__ is None and __name__ == '__main__':
    parent = pathlib.Path(__file__).absolute().parents[1]
    sys.path.insert(0, str(parent))
    __package__ = 'sacrebleu'

from .dataset import DATASETS
from .metrics import METRICS
from .utils import smart_open, filter_subset, get_langpairs_for_testset, get_available_testsets
from .utils import print_test_set, print_subset_results, get_reference_files, download_test_set
from .utils import args_to_dict, sanity_check_lengths, print_results_table, print_single_results
from .utils import get_available_testsets_for_langpair, Color

from . import __version__ as VERSION

sacrelogger = logging.getLogger('sacrebleu')

try:
    # SIGPIPE is not available on Windows machines, throwing an exception.
    from signal import SIGPIPE  # type: ignore

    # If SIGPIPE is available, change behaviour to default instead of ignore.
    from signal import signal, SIG_DFL
    signal(SIGPIPE, SIG_DFL)
except ImportError:
    pass


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description='sacreBLEU: Hassle-free computation of shareable BLEU scores.\n'
                    'Quick usage: score your detokenized output against WMT\'14 EN-DE:\n'
                    '    cat output.detok.de | sacrebleu -t wmt14 -l en-de',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    arg_parser.add_argument('--citation', '--cite', default=False, action='store_true',
                            help='Dump the bibtex citation and quit.')
    arg_parser.add_argument('--list', default=False, action='store_true',
                            help='Print a list of all available test sets.')
    arg_parser.add_argument('--test-set', '-t', type=str, default=None,
                            help='The test set to use (see also --list) or a comma-separated list of test sets to be concatenated.')
    arg_parser.add_argument('--language-pair', '-l', dest='langpair', default=None,
                            help='Source-target language pair (2-char ISO639-1 codes).')
    arg_parser.add_argument('--origlang', '-ol', dest='origlang', default=None,
                            help='Use a subset of sentences with a given original language (2-char ISO639-1 codes), "non-" prefix means negation.')
    arg_parser.add_argument('--subset', dest='subset', default=None,
                            help='Use a subset of sentences whose document annotation matches a given regex (see SUBSETS in the source code).')
    arg_parser.add_argument('--download', type=str, default=None,
                            help='Download a test set and quit.')
    arg_parser.add_argument('--echo', nargs="+", type=str, default=None,
                            help='Output the source (src), reference (ref), or other available field (docid, ref:A, ref:1 for example) to STDOUT and quit. '
                                 'You can get available fields with options `--list` and `-t`' 'For example: `sacrebleu -t wmt21 --list`. '
                                 'If multiple fields are given, they are outputted with tsv format in the order they are given.'
                                 'You can also use `--echo all` to output all available fields.')

    # I/O related arguments
    # Multiple input files can be provided for significance testing for example
    arg_parser.add_argument('--input', '-i', type=str, nargs='*', default=None,
                            help='Read input from file(s) instead of STDIN.')
    arg_parser.add_argument('refs', nargs='*', default=[],
                            help='Optional list of references. If given, it should preceed the -i/--input argument.')
    arg_parser.add_argument('--num-refs', '-nr', type=int, default=1,
                            help='Split the reference stream on tabs, and expect this many references. (Default: %(default)s)')
    arg_parser.add_argument('--encoding', '-e', type=str, default='utf-8',
                            help='Open text files with specified encoding (Default: %(default)s)')

    # Metric selection
    avail_metrics = [m.lower() for m in METRICS]
    arg_parser.add_argument('--metrics', '-m', choices=avail_metrics, nargs='+', default=['bleu'],
                            help='Space-delimited list of metrics to compute (Default: bleu)')
    arg_parser.add_argument('--sentence-level', '-sl', action='store_true', help='Compute metric for each sentence.')

    # BLEU-related arguments
    # since sacreBLEU had only support for BLEU initially, the argument names
    # are not prefixed with 'bleu' as in chrF arguments for example.
    # Let's do that manually here through dest= options, as otherwise
    # things will get quite hard to maintain when other metrics are added.
    bleu_args = arg_parser.add_argument_group('BLEU related arguments')

    bleu_args.add_argument('--smooth-method', '-s', choices=METRICS['BLEU'].SMOOTH_DEFAULTS.keys(), default='exp',
                           dest='bleu_smooth_method',
                           help='Smoothing method: exponential decay, floor (increment zero counts), add-k (increment num/denom by k for n>1), or none. (Default: %(default)s)')
    bleu_args.add_argument('--smooth-value', '-sv', type=float, default=None,
                           dest='bleu_smooth_value',
                           help='The smoothing value. Only valid for floor and add-k. '
                                f"(Defaults: floor: {METRICS['BLEU'].SMOOTH_DEFAULTS['floor']}, "
                                f"add-k: {METRICS['BLEU'].SMOOTH_DEFAULTS['add-k']})")
    bleu_args.add_argument('--tokenize', '-tok', choices=METRICS['BLEU'].TOKENIZERS, default=None,
                           dest='bleu_tokenize',
                           help='Tokenization method to use for BLEU. If not provided, defaults to `zh` for Chinese, '
                                '`ja-mecab` for Japanese, `ko-mecab` for Korean and `13a` (mteval) otherwise.')
    bleu_args.add_argument('--lowercase', '-lc', dest='bleu_lowercase', action='store_true', default=False,
                           help='If True, enables case-insensitivity. (Default: %(default)s)')
    bleu_args.add_argument('--force', default=False, action='store_true',
                           dest='bleu_force', help='Insist that your tokenized input is actually detokenized.')

    # ChrF-related arguments
    chrf_args = arg_parser.add_argument_group('chrF related arguments')
    chrf_args.add_argument('--chrf-char-order', '-cc', type=int, default=METRICS['CHRF'].CHAR_ORDER,
                           help='Character n-gram order. (Default: %(default)s)')
    chrf_args.add_argument('--chrf-word-order', '-cw', type=int, default=METRICS['CHRF'].WORD_ORDER,
                           help='Word n-gram order (Default: %(default)s). If equals to 2, the metric is referred to as chrF++.')
    chrf_args.add_argument('--chrf-beta', type=int, default=METRICS['CHRF'].BETA,
                           help='Determine the importance of recall w.r.t precision. (Default: %(default)s)')
    chrf_args.add_argument('--chrf-whitespace', action='store_true', default=False,
                           help='Include whitespaces when extracting character n-grams. (Default: %(default)s)')
    chrf_args.add_argument('--chrf-lowercase', action='store_true', default=False,
                           help='Enable case-insensitivity. (Default: %(default)s)')
    chrf_args.add_argument('--chrf-eps-smoothing', action='store_true', default=False,
                           help='Enables epsilon smoothing similar to chrF++.py, NLTK and Moses; instead of effective order smoothing. (Default: %(default)s)')

    # TER related arguments
    ter_args = arg_parser.add_argument_group("TER related arguments (The defaults replicate TERCOM's behavior)")
    ter_args.add_argument('--ter-case-sensitive', action='store_true',
                          help='Enables case sensitivity. (Default: %(default)s)')
    ter_args.add_argument('--ter-asian-support', action='store_true',
                          help='Enables special treatment of Asian characters. (Default: %(default)s)')
    ter_args.add_argument('--ter-no-punct', action='store_true',
                          help='Removes punctuation. (Default: %(default)s)')
    ter_args.add_argument('--ter-normalized', action='store_true',
                          help='Applies basic normalization and tokenization. (Default: %(default)s)')

    # Bootstrap resampling for confidence intervals
    sign_args = arg_parser.add_argument_group('Confidence interval (CI) estimation for single-system evaluation')
    sign_args.add_argument('--confidence', '-ci', action='store_true',
                           help='Report confidence interval using bootstrap resampling.')
    sign_args.add_argument('--confidence-n', '-cin', type=int, default=1000,
                           help='Set the number of bootstrap resamples for CI estimation (Default: %(default)s).')

    # Paired significance testing
    pair_args = arg_parser.add_argument_group('Paired significance testing for multi-system evaluation')
    pair_args_choice = pair_args.add_mutually_exclusive_group()

    pair_args_choice.add_argument('--paired-ar', '-par', action='store_true',
                                  help='Perform paired test using approximate randomization (AR). This option is '
                                       'mutually exclusive with --paired-bs (Default: %(default)s).')
    pair_args_choice.add_argument('--paired-bs', '-pbs', action='store_true',
                                  help='Perform paired test using bootstrap resampling. This option is '
                                       'mutually exclusive with --paired-ar (Default: %(default)s).')

    pair_args.add_argument('--paired-ar-n', '-parn', type=int, default=10000,
                           help='Number of trials for approximate randomization test (Default: %(default)s).')

    pair_args.add_argument('--paired-bs-n', '-pbsn', type=int, default=1000,
                           help='Number of bootstrap resamples for paired bootstrap resampling test (Default: %(default)s).')

    pair_args.add_argument('--paired-jobs', '-j', type=int, default=1,
                           help='If 0, launches as many workers as the number of systems. If > 0, sets the number of workers manually. '
                                'This feature is currently not supported on Windows.')

    # Reporting related arguments
    report_args = arg_parser.add_argument_group('Reporting related arguments')
    report_args.add_argument('--quiet', '-q', default=False, action='store_true',
                             help='Suppress verbose messages.')
    report_args.add_argument('--short', '-sh', default=False, action='store_true',
                             help='Produce a shorter (less human readable) signature.')
    report_args.add_argument('--score-only', '-b', default=False, action='store_true',
                             help='Print only the computed score.')
    report_args.add_argument('--width', '-w', type=int, default=1,
                             help='Floating point width (Default: %(default)s).')
    report_args.add_argument('--detail', '-d', default=False, action='store_true',
                             help='Print detailed information (split test sets based on origlang).')
    report_args.add_argument('--no-color', '-nc', action='store_true',
                             help='Disable the occasional use of terminal colors.')

    output_formats = ['json', 'text', 'latex']
    report_args.add_argument('--format', '-f', default='json', choices=output_formats,
                             help='Set the output format. `latex` is only valid for multi-system mode whereas '
                                  '`json` and `text` apply to single-system mode only. This flag is overridden if the '
                                  'SACREBLEU_FORMAT environment variable is set to one of the valid choices (Default: %(default)s).')

    arg_parser.add_argument('--version', '-V', action='version', version='%(prog)s {}'.format(VERSION))

    args = arg_parser.parse_args()

    # Override the format from the environment, if any
    if 'SACREBLEU_FORMAT' in os.environ:
        _new_value = os.environ['SACREBLEU_FORMAT'].lower()
        if _new_value in output_formats:
            args.format = _new_value

    return args


def main():
    args = parse_args()

    # Is paired test requested?
    paired_test_mode = args.paired_bs or args.paired_ar

    # Explicitly set the encoding
    sys.stdin = open(sys.stdin.fileno(), mode='r', encoding='utf-8', buffering=True, newline="\n")
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=True)

    if os.environ.get('NO_COLOR', False) or args.no_color:
        Color.ENABLE_COLORS = False
    else:
        # These should come after all stdout manipulations otherwise cause
        # issues esp. on Windows
        import colorama
        colorama.init()

    if not args.quiet:
        logging.basicConfig(level=logging.INFO, format='sacreBLEU: %(message)s')

    if args.download:
        download_test_set(args.download, args.langpair)
        sys.exit(0)

    if args.list:
        if args.test_set:
            for pair in [args.langpair] if args.langpair else get_langpairs_for_testset(args.test_set):
                fields = DATASETS[args.test_set].fieldnames(pair)
                print(f'{pair}: {", ".join(fields)}')
        else:
            if args.langpair:
                print(f'The available test sets for {args.langpair} are:')
                testsets = get_available_testsets_for_langpair(args.langpair)
            else:
                print('The available test sets are:')
                testsets = get_available_testsets()
            for testset in sorted(testsets):
                desc = DATASETS[testset].description.strip()
                print(f'{testset:<30}: {desc}')
        sys.exit(0)

    if args.sentence_level and len(args.metrics) > 1:
        sacrelogger.error('Only one metric can be used in sentence-level mode.')
        sys.exit(1)

    if args.citation:
        if not args.test_set:
            sacrelogger.error('I need a test set (-t).')
            sys.exit(1)
        for test_set in args.test_set.split(','):
            if 'citation' not in DATASETS[test_set]:
                sacrelogger.error(f'No citation found for {test_set}')
            else:
                print(DATASETS[test_set].citation)
        sys.exit(0)

    if args.num_refs != 1 and (args.test_set is not None or len(args.refs) > 1):
        sacrelogger.error('The --num-refs argument allows you to provide any number of tab-delimited references in a single file.')
        sacrelogger.error('You can only use it with externally provided references, however (i.e., not with `-t`),')
        sacrelogger.error('and you cannot then provide multiple reference files.')
        sys.exit(1)

    if args.test_set is not None:
        for test_set in args.test_set.split(','):
            if test_set not in DATASETS:
                sacrelogger.error(f'Unknown test set {test_set!r}')
                sacrelogger.error('Please run with --list to see the available test sets.')
                sys.exit(1)

    if args.test_set is None:
        if len(args.refs) == 0:
            sacrelogger.error('If manual references given, make sure to provide them '
                              'before the -i/--input argument to avoid confusion.')
            sacrelogger.error('Otherwise, I need a predefined test set (-t) from the following list:')
            sacrelogger.error(get_available_testsets())
            sys.exit(1)
    elif len(args.refs) > 0:
        sacrelogger.error('I need exactly one of (a) a predefined test set (-t) or (b) a list of references')
        sys.exit(1)
    elif args.langpair is None:
        sacrelogger.error('I need a language pair (-l). Use --list to see available language pairs for this test set.')
        sys.exit(1)
    else:
        for test_set in args.test_set.split(','):
            langpairs = get_langpairs_for_testset(test_set)
            if args.langpair not in langpairs:
                sacrelogger.error(f'No such language pair {args.langpair!r}')
                sacrelogger.error(f'Available language pairs for {test_set!r} are:')
                for lp in langpairs:
                    sacrelogger.error(f' > {lp}')
                sys.exit(1)

    if args.echo:
        if args.langpair is None or args.test_set is None:
            sacrelogger.warning("--echo requires a test set (--t) and a language pair (-l)")
            sys.exit(1)
        for test_set in args.test_set.split(','):
            print_test_set(test_set, args.langpair, args.echo, args.origlang, args.subset)
        sys.exit(0)

    # Hack: inject target language info for BLEU, so that it can
    # select the tokenizer based on it
    if args.langpair:
        args.bleu_trg_lang = args.langpair.split('-')[1]

    if args.test_set is not None and args.bleu_tokenize == 'none':
        sacrelogger.warning(
            "You are turning off BLEU's internal tokenizer "
            "presumably to supply your own tokenized files.")
        sacrelogger.warning(
            "Published numbers will not be comparable to other papers.")

    # concat_ref_files is a list of list of reference filenames
    # (concatenation happens if multiple test sets are given through -t)
    # Example: [[testset1_refA, testset1_refB], [testset2_refA, testset2_refB]]
    concat_ref_files = []
    if args.test_set is None:
        concat_ref_files.append(args.refs)
    else:
        # Multiple test sets can be given
        for test_set in args.test_set.split(','):
            ref_files = get_reference_files(test_set, args.langpair)
            if len(ref_files) == 0:
                sacrelogger.warning(
                    f'No references found for test set {test_set}/{args.langpair}.')
            concat_ref_files.append(ref_files)

    #################
    # Read references
    #################
    full_refs = [[] for x in range(max(len(concat_ref_files[0]), args.num_refs))]
    for ref_files in concat_ref_files:
        for refno, ref_file in enumerate(ref_files):
            for lineno, line in enumerate(smart_open(ref_file, encoding=args.encoding), 1):
                line = line.rstrip()
                if args.num_refs == 1:
                    full_refs[refno].append(line)
                else:
                    refs = line.split(sep='\t', maxsplit=args.num_refs - 1)
                    # We are strict in fixed number of references through CLI
                    # But the API supports having variable refs per each segment
                    # by simply having '' or None's as dummy placeholders
                    if len(refs) != args.num_refs:
                        sacrelogger.error(f'FATAL: line {lineno}: expected {args.num_refs} fields, but found {len(refs)}.')
                        sys.exit(17)
                    for refno, ref in enumerate(refs):
                        full_refs[refno].append(ref)

    # Decide on the number of final references, override the argument
    args.num_refs = len(full_refs)

    # Read hypotheses
    # Can't tokenize yet as each metric has its own way of tokenizing things
    full_systems, sys_names = [], []

    if args.input is None:
        # Read from STDIN
        inputfh = io.TextIOWrapper(sys.stdin.buffer, encoding=args.encoding)

        # guess the number of systems by looking at the first line
        fields = inputfh.readline().rstrip().split('\t')

        # Set number of systems
        num_sys = len(fields)

        # place the first lines already
        full_systems = [[s] for s in fields]

        # Enumerate the systems
        sys_names = [f'System {i + 1}' for i in range(num_sys)]

        # Read the rest
        for line in inputfh:
            fields = line.rstrip().split('\t')
            if len(fields) != num_sys:
                sacrelogger.error('FATAL: the number of tab-delimited fields in the input stream differ across lines.')
                sys.exit(17)
            # Place systems into the list
            for sys_idx, sent in enumerate(fields):
                full_systems[sys_idx].append(sent.rstrip())
    else:
        # Separate files are given for each system output
        # Ex: --input smt.txt nmt.txt
        for fname in args.input:
            sys_name = fname

            if sys_name in sys_names:
                if paired_test_mode and sys_name == sys_names[0]:
                    # We skip loading a system, if it was already the baseline
                    sacrelogger.info(f'Ignoring {sys_name!r} as it was also given as the baseline.')
                    continue
                else:
                    # To avoid ambiguities, we fail if two systems have same names
                    sacrelogger.error(f"{sys_name!r} already used to name a system.")
                    sacrelogger.error("Make sure to have a different basename for each system.")
                    sys.exit(1)

            # Read the system
            lines = []
            for line in smart_open(fname, encoding=args.encoding):
                lines.append(line.rstrip())
            full_systems.append(lines)
            sys_names.append(sys_name)

        # Set final number of systems
        num_sys = len(sys_names)

    # Add baseline prefix to the first system for clarity
    if paired_test_mode:
        if args.input is None:
            # STDIN mode, no explicit system names
            sys_names = ['Baseline'] + [f'System {i + 1}' for i in range(num_sys - 1)]
        else:
            # --input mode, we have names for the systems, just change the 1st one
            sys_names[0] = f'Baseline: {sys_names[0]}'

    if args.sentence_level:
        if num_sys > 1:
            sacrelogger.error('Only one system can be evaluated in sentence-level mode.')
            sys.exit(1)
        if args.confidence or paired_test_mode:
            sacrelogger.error('Statistical tests are unavailable in sentence-level mode.')
            sys.exit(1)

        # >=2.0.0: effective_order is now part of BLEU class. For sentence-BLEU
        # we now need to explicitly enable it without user's intervention
        # for backward compatibility.
        args.bleu_effective_order = True

    if paired_test_mode and num_sys == 1:
        sacrelogger.error('Paired tests require multiple input systems given to --input (-i).')
        sys.exit(1)

    if num_sys > 1 and args.confidence:
        sacrelogger.error('Use paired tests (--paired) for multiple systems.')
        sys.exit(1)

    # Filter subsets if requested
    outputs = filter_subset(
        [*full_systems, *full_refs], args.test_set, args.langpair,
        args.origlang, args.subset)

    # Unpack systems & references back
    systems, refs = outputs[:num_sys], outputs[num_sys:]

    # Perform some sanity checks
    for system in systems:
        if len(system) == 0:
            message = f'Test set {args.test_set!r} contains no sentence'
            if args.origlang is not None or args.subset is not None:
                message += ' with'
                if args.origlang:
                    message += f' origlang={args.origlang}'
                if args.subset:
                    message += f' subset={args.subset}' + args.subset
            sacrelogger.error(message)
            sys.exit(1)

        # Check lengths
        sanity_check_lengths(system, refs, test_set=args.test_set)

    # Create the metrics
    metrics = {}
    for name in args.metrics:
        # Each metric's specific arguments are prefixed with `metricname_`
        # for grouping. Filter accordingly and strip the prefixes prior to
        # metric object construction.
        metric_args = args_to_dict(args, name.lower(), strip_prefix=True)

        # This will cache reference stats for faster re-computation if required
        metric_args['references'] = refs

        # Make it uppercase for the rest of the code
        name = name.upper()
        metrics[name] = METRICS[name](**metric_args)

    # Handle sentence level and quit
    if args.sentence_level:
        # one metric and one system in use for sentence-level
        metric, system = list(metrics.values())[0], systems[0]

        for hypothesis, *references in zip(system, *refs):
            score = metric.sentence_score(hypothesis, references)
            sig = metric.get_signature().format(args.short)
            print(score.format(args.width, args.score_only, sig))

        sys.exit(0)

    if args.detail and args.format == 'json':
        # The translationese info will interfere with JSON output, disable
        args.format = 'text'

    ##############################
    # Corpus level evaluation mode
    ##############################
    if num_sys == 1:
        # Single system evaluation mode
        results = []
        for name in sorted(metrics):
            # compute the score
            score = metrics[name].corpus_score(
                system, references=None,
                n_bootstrap=args.confidence_n if args.confidence else 1)
            # get the signature
            sig = metrics[name].get_signature().format(
                args.short if args.format != 'json' else False)
            results.append(
                score.format(args.width, args.score_only, sig, args.format == 'json'))

        print_single_results(results, args)

        # Prints detailed information for translationese effect experiments
        if args.detail:
            print_subset_results(metrics, full_systems[0], full_refs, args)
    else:
        # Multi-system evaluation mode
        named_systems = [(sys_names[i], systems[i]) for i in range(num_sys)]
        sacrelogger.info(f'Found {num_sys} systems.')

        if not paired_test_mode:
            # Bootstrap resampling or the usual single score computation mode
            sigs = {}
            scores = defaultdict(list)
            scores['System'] = sys_names

            for sys_name, system in named_systems:
                for name in sorted(metrics):
                    score = metrics[name].corpus_score(system, references=None)
                    sigs[score.name] = metrics[name].get_signature().format(args.short)
                    scores[score.name].append(score.format(args.width, True))

        else:
            # Paired significance testing mode
            from .significance import PairedTest

            # Set params
            test_type = 'bs' if args.paired_bs else 'ar'
            n_samples = args.paired_bs_n if args.paired_bs else args.paired_ar_n

            ps = PairedTest(named_systems, metrics, references=None,
                            test_type=test_type, n_samples=n_samples,
                            n_jobs=args.paired_jobs)

            # Set back the number of trials
            args.paired_n = ps.n_samples

            # Run the test
            sigs, scores = ps()

            # Get signature strings
            sigs = {k: v.format(args.short) for k, v in sigs.items()}

        # Dump the results
        print_results_table(scores, sigs, args)


if __name__ == '__main__':
    main()
