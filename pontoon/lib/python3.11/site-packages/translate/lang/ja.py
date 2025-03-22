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
This module represents the Japanese language.

.. seealso:: :wp:`Japanese_language`
"""

import re

from translate.lang import common


class ja(common.Common):
    """This class represents Japanese."""

    listseperator = "、､，,"

    sentenceend = "。｡！？!?…"

    # Compared to common.py, we make the space after the sentence ending
    # optional and don't demand an uppercase letter to follow.
    sentencere = re.compile(
        rf"""(?s)    #make . also match newlines
                            .*?         #any text, but match non-greedy
                            [{sentenceend}]        #the puntuation for sentence ending
                            \s*         #the optional space after the puntuation
                            """,
        re.VERBOSE,
    )

    puncdict = {
        ". ": "。",
        ", ": "、",
        ".\n": "。\n",
        ",\n": "、\n",
    }

    ignoretests = {
        "all": ["simplecaps", "startcaps"],
    }
