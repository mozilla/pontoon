# -*- coding: utf-8 -*-

import os
from copy import deepcopy
from functools import partial
from functools import update_wrapper

import click

from sacremoses.tokenize import MosesTokenizer, MosesDetokenizer
from sacremoses.truecase import MosesTruecaser, MosesDetruecaser
from sacremoses.normalize import MosesPunctNormalizer
from sacremoses.util import parallelize_preprocess

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(chain=True, context_settings=CONTEXT_SETTINGS)
@click.option(
    "--language", "-l", default="en", help="Use language specific rules when tokenizing"
)
@click.option("--processes", "-j", default=1, help="No. of processes.")
@click.option("--encoding", "-e", default="utf8", help="Specify encoding of file.")
@click.option(
    "--quiet", "-q", is_flag=True, default=False, help="Disable progress bar."
)
@click.version_option()
def cli(language, encoding, processes, quiet):
    pass


# TODO: Get rid of this when it's possible.
# https://github.com/alvations/sacremoses/issues/130
result_callback = cli.resultcallback if int(click.__version__.split('.')[0]) < 8 else cli.result_callback

@result_callback()
def process_pipeline(processors, encoding, **kwargs):
    with click.get_text_stream("stdin", encoding=encoding) as fin:
        iterator = fin  # Initialize fin as the first iterator.
        for proc in processors:
            iterator = proc(list(iterator), **kwargs)
        if iterator:
            for item in iterator:
                click.echo(item)


def processor(f, **kwargs):
    """Helper decorator to rewrite a function so that
    it returns another function from it.
    """

    def new_func(**kwargs):
        def processor(stream, **kwargs):
            return f(stream, **kwargs)

        return partial(processor, **kwargs)

    return update_wrapper(new_func, f, **kwargs)


def parallel_or_not(iterator, func, processes, quiet):
    if processes == 1:
        for line in iterator:
            yield func(line)
    else:
        for outline in parallelize_preprocess(
            func, iterator, processes, progress_bar=(not quiet)
        ):
            yield outline


########################################################################
# Tokenize
########################################################################


@cli.command("tokenize")
@click.option(
    "--aggressive-dash-splits",
    "-a",
    default=False,
    is_flag=True,
    help="Triggers dash split rules.",
)
@click.option(
    "--xml-escape",
    "-x",
    default=True,
    is_flag=True,
    help="Escape special characters for XML.",
)
@click.option(
    "--protected-patterns",
    "-p",
    help="Specify file with patters to be protected in tokenisation. Special values: :basic: :web:",
)
@click.option(
    "--custom-nb-prefixes",
    "-c",
    help="Specify a custom non-breaking prefixes file, add prefixes to the default ones from the specified language.",
)
@processor
def tokenize_file(
    iterator,
    language,
    processes,
    quiet,
    xml_escape,
    aggressive_dash_splits,
    protected_patterns,
    custom_nb_prefixes,
):
    moses = MosesTokenizer(
        lang=language, custom_nonbreaking_prefixes_file=custom_nb_prefixes
    )

    if protected_patterns:
        if protected_patterns == ":basic:":
            protected_patterns = moses.BASIC_PROTECTED_PATTERNS
        elif protected_patterns == ":web:":
            protected_patterns = moses.WEB_PROTECTED_PATTERNS
        else:
            with open(protected_patterns, encoding="utf8") as fin:
                protected_patterns = [pattern.strip() for pattern in fin.readlines()]

    moses_tokenize = partial(
        moses.tokenize,
        return_str=True,
        aggressive_dash_splits=aggressive_dash_splits,
        escape=xml_escape,
        protected_patterns=protected_patterns,
    )
    return parallel_or_not(iterator, moses_tokenize, processes, quiet)


########################################################################
# Detokenize
########################################################################


@cli.command("detokenize")
@click.option(
    "--xml-unescape",
    "-x",
    default=True,
    is_flag=True,
    help="Unescape special characters for XML.",
)
@processor
def detokenize_file(
    iterator,
    language,
    processes,
    quiet,
    xml_unescape,
):
    moses = MosesDetokenizer(lang=language)
    moses_detokenize = partial(moses.detokenize, return_str=True, unescape=xml_unescape)
    return parallel_or_not(
        list(map(str.split, iterator)), moses_detokenize, processes, quiet
    )


########################################################################
# Normalize
########################################################################


@cli.command("normalize")
@click.option(
    "--normalize-quote-commas",
    "-q",
    default=True,
    is_flag=True,
    help="Normalize quotations and commas.",
)
@click.option(
    "--normalize-numbers", "-d", default=True, is_flag=True, help="Normalize number."
)
@click.option(
    "--replace-unicode-puncts",
    "-p",
    default=False,
    is_flag=True,
    help="Replace unicode punctuations BEFORE normalization.",
)
@click.option(
    "--remove-control-chars",
    "-c",
    default=False,
    is_flag=True,
    help="Remove control characters AFTER normalization.",
)
@processor
def normalize_file(
    iterator,
    language,
    processes,
    quiet,
    normalize_quote_commas,
    normalize_numbers,
    replace_unicode_puncts,
    remove_control_chars,
):
    moses = MosesPunctNormalizer(
        language,
        norm_quote_commas=normalize_quote_commas,
        norm_numbers=normalize_numbers,
        pre_replace_unicode_punct=replace_unicode_puncts,
        post_remove_control_chars=remove_control_chars,
    )
    moses_normalize = partial(moses.normalize)
    return parallel_or_not(iterator, moses_normalize, processes, quiet)


########################################################################
# Train Truecase
########################################################################


@cli.command("train-truecase")
@click.option(
    "--modelfile", "-m", required=True, help="Filename to save the modelfile."
)
@click.option(
    "--is-asr",
    "-a",
    default=False,
    is_flag=True,
    help="A flag to indicate that model is for ASR.",
)
@click.option(
    "--possibly-use-first-token",
    "-p",
    default=False,
    is_flag=True,
    help="Use the first token as part of truecasing.",
)
@processor
def train_truecaser(
    iterator, language, processes, quiet, modelfile, is_asr, possibly_use_first_token
):
    moses = MosesTruecaser(is_asr=is_asr)
    # iterator_copy = deepcopy(iterator)
    model = moses.train(
        iterator,
        possibly_use_first_token=possibly_use_first_token,
        processes=processes,
        progress_bar=(not quiet),
    )
    moses.save_model(modelfile)


########################################################################
# Truecase
########################################################################


@cli.command("truecase")
@click.option(
    "--modelfile", "-m", required=True, help="Filename to save/load the modelfile."
)
@click.option(
    "--is-asr",
    "-a",
    default=False,
    is_flag=True,
    help="A flag to indicate that model is for ASR.",
)
@click.option(
    "--possibly-use-first-token",
    "-p",
    default=False,
    is_flag=True,
    help="Use the first token as part of truecase training.",
)
@processor
def truecase_file(
    iterator, language, processes, quiet, modelfile, is_asr, possibly_use_first_token
):
    # If model file doesn't exists, train a model.
    if not os.path.isfile(modelfile):
        iterator_copy = deepcopy(iterator)
        truecaser = MosesTruecaser(is_asr=is_asr)
        model = truecaser.train(
            iterator_copy,
            possibly_use_first_token=possibly_use_first_token,
            processes=processes,
            progress_bar=(not quiet),
        )
        truecaser.save_model(modelfile)
    # Truecase the file.
    moses = MosesTruecaser(load_from=modelfile, is_asr=is_asr)
    moses_truecase = partial(moses.truecase, return_str=True)
    return parallel_or_not(iterator, moses_truecase, processes, quiet)


########################################################################
# Detruecase
########################################################################


@cli.command("detruecase")
@click.option(
    "--is-headline",
    "-a",
    default=False,
    is_flag=True,
    help="Whether the file are headlines.",
)
@processor
def detruecase_file(iterator, language, processes, quiet, is_headline):
    moses = MosesDetruecaser()
    moses_detruecase = partial(
        moses.detruecase, return_str=True, is_headline=is_headline
    )
    return parallel_or_not(iterator, moses_detruecase, processes, quiet)
