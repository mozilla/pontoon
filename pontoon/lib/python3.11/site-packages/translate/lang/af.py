#
# Copyright 2007 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
This module represents the Afrikaans language.

.. seealso:: :wp:`Afrikaans_language`
"""

import re

from translate.lang import common

articlere = re.compile(r"'n\b")


class af(common.Common):
    """This class represents Afrikaans."""

    validdoublewords = [""]

    punctuation = (
        f"{common.Common.commonpunc}{common.Common.quotes}{common.Common.miscpunc}"
    )
    sentenceend = ".!?…"
    sentencere = re.compile(
        rf"""
        (?s)        # make . also match newlines
        .*?         # anything, but match non-greedy
        [{sentenceend}]        # the puntuation for sentence ending
        \s+         # the spacing after the puntuation
        (?='n\s[A-Z]|[^'a-z\d]|'[^n])
        # lookahead that next part starts with caps or 'n followed by caps
        """,
        re.VERBOSE,
    )

    specialchars = "ëïêôûáéíóúý"

    @classmethod
    def capsstart(cls, text):
        """Modify this for the indefinite article ('n)."""
        match = articlere.search(text, 0, 20)
        if match:
            # construct a list of non-apostrophe punctuation:
            nonapos = "".join(cls.punctuation.split("'"))
            stripped = text.lstrip().lstrip(nonapos)
            match = articlere.match(stripped)
            if match:
                return common.Common.capsstart(stripped[match.end() :])
        return common.Common.capsstart(text)


cyr2lat = {
    "А": "A",
    "а": "a",
    "Б": "B",
    "б": "b",
    "В": "W",
    "в": "w",  # Different if at the end of a syllable see rule 2.
    "Г": "G",
    "г": "g",  # see rule 3 and 4
    "Д": "D",
    "д": "d",
    "ДЖ": "Dj",
    "дж": "dj",
    "Е": "Je",
    "е": "je",  # Sometimes e need to check when/why see rule 5.
    "Ё": "Jo",
    "ё": "jo",  # see rule 6
    "ЕЙ": "Ei",
    "ей": "ei",
    "Ж": "Zj",
    "ж": "zj",
    "З": "Z",
    "з": "z",
    "И": "I",
    "и": "i",
    "Й": "J",
    "й": "j",  # see rule 9 and 10
    "К": "K",
    "к": "k",  # see note 11
    "Л": "L",
    "л": "l",
    "М": "M",
    "м": "m",
    "Н": "N",
    "н": "n",
    "О": "O",
    "о": "o",
    "П": "P",
    "п": "p",
    "Р": "R",
    "р": "r",
    "С": "S",
    "с": "s",  # see note 12
    "Т": "T",
    "т": "t",
    "У": "Oe",
    "у": "oe",
    "Ф": "F",
    "ф": "f",
    "Х": "Ch",
    "х": "ch",  # see rule 12
    "Ц": "Ts",
    "ц": "ts",
    "Ч": "Tj",
    "ч": "tj",
    "Ш": "Sj",
    "ш": "sj",
    "Щ": "Sjtsj",
    "щ": "sjtsj",
    "Ы": "I",
    "ы": "i",  # see note 13
    "Ъ": "",
    "ъ": "",  # See note 14
    "Ь": "",
    "ь": "",  # this letter is not in the AWS we assume it is left out as in the previous letter
    "Э": "E",
    "э": "e",
    "Ю": "Joe",
    "ю": "joe",
    "Я": "Ja",
    "я": "ja",
}
"""Mapping of Cyrillic to Latin letters for transliteration in Afrikaans"""

cyr_vowels = "аеёиоуыэюя"


def tranliterate_cyrillic(text):
    """Convert Cyrillic text to Latin according to the AWS transliteration rules."""
    trans = ""
    for i in text:
        trans += cyr2lat.get(i, i)
    return trans
