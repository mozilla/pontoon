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


import re
from functools import lru_cache

from .tokenizer_base import BaseTokenizer


def _normalize_general_and_western(sent: str) -> str:
    # language-independent (general) part

    # strip end-of-line hyphenation and join lines
    sent = re.sub(r"\n-", "", sent)

    # join lines
    sent = re.sub(r"\n", " ", sent)

    # handle XML escaped symbols
    sent = re.sub(r"&quot;", "\"", sent)
    sent = re.sub(r"&amp;", "&", sent)
    sent = re.sub(r"&lt;", "<", sent)
    sent = re.sub(r"&gt;", ">", sent)

    # language-dependent (Western) part
    sent = f" {sent} "

    # tokenize punctuation
    sent = re.sub(r"([{-~[-` -&(-+:-@/])", r" \1 ", sent)

    # handle possesives
    sent = re.sub(r"'s ", r" 's ", sent)
    sent = re.sub(r"'s$", r" 's", sent)

    # tokenize period and comma unless preceded by a digit
    sent = re.sub(r"([^0-9])([\.,])", r"\1 \2 ", sent)

    # tokenize period and comma unless followed by a digit
    sent = re.sub(r"([\.,])([^0-9])", r" \1 \2", sent)

    # tokenize dash when preceded by a digit
    sent = re.sub(r"([0-9])(-)", r"\1 \2 ", sent)

    return sent


def _normalize_asian(sent: str) -> str:
    # Split Chinese chars and Japanese kanji down to character level

    # 4E00—9FFF CJK Unified Ideographs
    # 3400—4DBF CJK Unified Ideographs Extension A
    sent = re.sub(r"([\u4e00-\u9fff\u3400-\u4dbf])", r" \1 ", sent)

    # 31C0—31EF CJK Strokes
    # 2E80—2EFF CJK Radicals Supplement
    sent = re.sub(r"([\u31c0-\u31ef\u2e80-\u2eff])", r" \1 ", sent)

    # 3300—33FF CJK Compatibility
    # F900—FAFF CJK Compatibility Ideographs
    # FE30—FE4F CJK Compatibility Forms
    sent = re.sub(
        r"([\u3300-\u33ff\uf900-\ufaff\ufe30-\ufe4f])", r" \1 ", sent)

    # 3200—32FF Enclosed CJK Letters and Months
    sent = re.sub(r"([\u3200-\u3f22])", r" \1 ", sent)

    # Split Hiragana, Katakana, and KatakanaPhoneticExtensions
    # only when adjacent to something else
    # 3040—309F Hiragana
    # 30A0—30FF Katakana
    # 31F0—31FF Katakana Phonetic Extensions
    sent = re.sub(
        r"(^|^[\u3040-\u309f])([\u3040-\u309f]+)(?=$|^[\u3040-\u309f])",
        r"\1 \2 ", sent)
    sent = re.sub(
        r"(^|^[\u30a0-\u30ff])([\u30a0-\u30ff]+)(?=$|^[\u30a0-\u30ff])",
        r"\1 \2 ", sent)
    sent = re.sub(
        r"(^|^[\u31f0-\u31ff])([\u31f0-\u31ff]+)(?=$|^[\u31f0-\u31ff])",
        r"\1 \2 ", sent)

    sent = re.sub(TercomTokenizer.ASIAN_PUNCT, r" \1 ", sent)
    sent = re.sub(TercomTokenizer.FULL_WIDTH_PUNCT, r" \1 ", sent)
    return sent


def _remove_punct(sent: str) -> str:
    return re.sub(r"[\.,\?:;!\"\(\)]", "", sent)


def _remove_asian_punct(sent: str) -> str:
    sent = re.sub(TercomTokenizer.ASIAN_PUNCT, r"", sent)
    sent = re.sub(TercomTokenizer.FULL_WIDTH_PUNCT, r"", sent)
    return sent


class TercomTokenizer(BaseTokenizer):
    """Re-implementation of Tercom Tokenizer in Python 3.

    See src/ter/core/Normalizer.java in https://github.com/jhclark/tercom

    Note that Python doesn't support named Unicode blocks so the mapping for
    relevant blocks was taken from here:

    https://unicode-table.com/en/blocks/
    """
    ASIAN_PUNCT = r"([\u3001\u3002\u3008-\u3011\u3014-\u301f\uff61-\uff65\u30fb])"
    FULL_WIDTH_PUNCT = r"([\uff0e\uff0c\uff1f\uff1a\uff1b\uff01\uff02\uff08\uff09])"

    def __init__(self,
                 normalized: bool = False,
                 no_punct: bool = False,
                 asian_support: bool = False,
                 case_sensitive: bool = False):
        """Initialize the tokenizer.

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
        :param case_sensitive: Enable case sensitivity, i.e., do not lower case data.
        """
        self._normalized = normalized
        self._no_punct = no_punct
        self._asian_support = asian_support
        self._case_sensitive = case_sensitive

    @lru_cache(maxsize=2**16)
    # Although the cache is shared across different instances, same sentence
    # queries do not return invalid returns across different instances since
    # `self` becomes part of the query as well.
    def __call__(self, sent: str) -> str:
        if not sent:
            return ""

        if not self._case_sensitive:
            sent = sent.lower()

        if self._normalized:
            sent = _normalize_general_and_western(sent)
            if self._asian_support:
                sent = _normalize_asian(sent)

        if self._no_punct:
            sent = _remove_punct(sent)
            if self._asian_support:
                sent = _remove_asian_punct(sent)

        # Strip extra whitespaces
        return ' '.join(sent.split())

    def signature(self):
        return 'tercom'
