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
This module represents the Chinese language (Both tradisional and simplified).

.. seealso:: :wp:`Chinese_language`
"""

import re

from translate.lang import common


class zh(common.Common):
    """This class represents Chinese."""

    listseperator = "、"

    sentenceend = "。！？!?…"

    # Compared to common.py, we make the space after the sentence ending
    # optional and don't demand an uppercase letter to follow.
    sentencere = re.compile(
        rf"""(?s) # make . also match newlines
                            .*?      # any text, but match non-greedy
                            [{sentenceend}]     # the puntuation for sentence ending
                            \s*      # the optional space after the puntuation
                            """,
        re.VERBOSE,
    )

    # The following transformation rules should be mostly useful for all types
    # of Chinese. The comma (,) is not handled here, since it maps to two
    # different characters, depending on context.
    # If comma is used as seperation of sentence, it should be converted to a
    # fullwidth comma ("，"). If comma is used as seperation of list items
    # like "apple, orange, grape, .....", "、" is used.
    puncdict = {
        ". ": "。",
        "; ": "；",
        ": ": "：",
        "! ": "！",
        "? ": "？",
        ".\n": "。\n",
        ";\n": "；\n",
        ":\n": "：\n",
        "!\n": "！\n",
        "?\n": "？",
        "% ": "%",
    }

    @classmethod
    def length_difference(cls, length):
        return 10 - length / 2

    ignoretests = {
        "all": ["simplecaps", "startcaps"],
    }
