#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

__description__ = "Hassle-free computation of shareable, comparable, and reproducible BLEU, chrF, and TER scores"


# Backward compatibility functions for old style API access (<= 1.4.10)
from .compat import (
    corpus_bleu,
    corpus_chrf,
    corpus_ter,
    raw_corpus_bleu,
    sentence_bleu,
    sentence_chrf,
    sentence_ter,
)
from .dataset import DATASETS
from .metrics import BLEU, CHRF, TER
from .metrics.helpers import extract_char_ngrams, extract_word_ngrams
from .utils import (
    SACREBLEU_DIR,
    download_test_set,
    get_available_testsets,
    get_langpairs_for_testset,
    get_reference_files,
    get_source_file,
    smart_open,
)
from .version import __version__

__all__ = [
    "smart_open",
    "SACREBLEU_DIR",
    "download_test_set",
    "get_source_file",
    "get_reference_files",
    "get_available_testsets",
    "get_langpairs_for_testset",
    "extract_word_ngrams",
    "extract_char_ngrams",
    "DATASETS",
    "BLEU",
    "CHRF",
    "TER",
    "corpus_bleu",
    "raw_corpus_bleu",
    "sentence_bleu",
    "corpus_chrf",
    "sentence_chrf",
    "corpus_ter",
    "sentence_ter",
    "__version__",
]
