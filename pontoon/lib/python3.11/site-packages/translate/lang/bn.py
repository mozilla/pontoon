#
# Copyright 2008 Zuza Software Foundation
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
This module represents the Bengali language.

.. seealso:: :wp:`Bengali_language`
"""

import re

from translate.lang import common


class bn(common.Common):
    """This class represents Bengali."""

    sentenceend = "।!?…"

    sentencere = re.compile(
        rf"""(?s)    #make . also match newlines
                            .*?         #anything, but match non-greedy
                            [{sentenceend}]        #the puntuation for sentence ending
                            \s+         #the spacing after the puntuation
                            (?=[^a-z\d])#lookahead that next part starts with caps
                            """,
        re.VERBOSE,
    )

    puncdict = {
        ". ": "। ",
        ".\n": "।\n",
    }

    numbertuple = (
        ("0", "০"),  # U+09E6 Bengali digit zero.
        ("1", "১"),  # U+09E7 Bengali digit one.
        ("2", "২"),  # U+09E8 Bengali digit two.
        ("3", "৩"),  # U+09E9 Bengali digit three.
        ("4", "৪"),  # U+09EA Bengali digit four.
        ("5", "৫"),  # U+09EB Bengali digit five.
        ("6", "৬"),  # U+09EC Bengali digit six.
        ("7", "৭"),  # U+09ED Bengali digit seven.
        ("8", "৮"),  # U+09EE Bengali digit eight.
        ("9", "৯"),  # U+09EF Bengali digit nine.
    )

    ignoretests = {
        "all": ["simplecaps", "startcaps"],
    }
