#
# Copyright 2007-2009,2011 Zuza Software Foundation
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
This module represents the Greek language.

.. seealso:: :wp:`Greek_language`
"""

import re

from translate.lang import common


class el(common.Common):
    """This class represents Greek."""

    # Greek uses ; as question mark and the middot instead
    sentenceend = ".!;…"

    sentencere = re.compile(
        rf"""
        (?s)        # make . also match newlines
        .*?         # anything, but match non-greedy
        [{sentenceend}]        # the puntuation for sentence ending
        \s+         # the spacing after the puntuation
        (?=[^a-zά-ώ\d])  # lookahead that next part starts with caps
        """,
        re.VERBOSE | re.UNICODE,
    )

    puncdict = {
        ";": "·",
        "?": ";",
    }

    # Valid latin characters for use as accelerators
    valid_latin_accel = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    # Valid greek characters for use as accelerators (accented characters
    # and "ς" omitted)
    valid_greek_accel = "αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"

    # Valid accelerators
    validaccel = f"{valid_latin_accel}{valid_greek_accel}"
