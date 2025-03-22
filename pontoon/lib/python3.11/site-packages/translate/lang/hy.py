#
# Copyright 2007-2008, 2011 Zuza Software Foundation
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
This module represents the Armenian language.

.. seealso:: :wp:`Armenian_language`
"""

import re

from translate.lang import common


class hy(common.Common):
    """This class represents Armenian."""

    armenianpunc = "։՝՜՞"

    punctuation = f"{common.Common.commonpunc}{common.Common.quotes}{common.Common.miscpunc}{armenianpunc}"

    sentenceend = "։՝՜…"

    sentencere = re.compile(
        rf"""
        (?s)        # make . also match newlines
        .*?         # anything, but match non-greedy
        [{sentenceend}]        # the puntuation for sentence ending
        \s+         # the spacing after the puntuation
        (?=[^a-zա-ֆ\d])  # lookahead that next part starts with caps
        """,
        re.VERBOSE | re.UNICODE,
    )

    puncdict = {
        ".": "։",
        ":": "՝",
        "!": "՜",
        "?": "՞",
    }

    ignoretests = {
        "all": ["simplecaps", "startcaps"],
    }

    mozilla_nplurals = 2
    mozilla_pluralequation = "n!=1 ? 1 : 0"
