#
# Copyright 2007,2009,2011 Zuza Software Foundation
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
This module represents the Arabic language.

.. seealso:: :wp:`Arabic_language`
"""

import re

from translate.lang import common


def reverse_quotes(text):
    def convertquotation(match):
        return f"”{match.group(1)}“"

    return re.sub("“([^”]+)”", convertquotation, text)


class ar(common.Common):
    """This class represents Arabic."""

    listseperator = "، "

    puncdict = {
        ",": "،",
        ";": "؛",
        "?": "؟",
        # This causes problems with variables, so commented out for now:
        # "%": "٪",
    }

    numbertuple = (
        ("0", "٠"),  # U+0660 Arabic-Indic digit zero.
        ("1", "١"),  # U+0661 Arabic-Indic digit one.
        ("2", "٢"),  # U+0662 Arabic-Indic digit two.
        ("3", "٣"),  # U+0663 Arabic-Indic digit three.
        ("4", "٤"),  # U+0664 Arabic-Indic digit four.
        ("5", "٥"),  # U+0665 Arabic-Indic digit five.
        ("6", "٦"),  # U+0666 Arabic-Indic digit six.
        ("7", "٧"),  # U+0667 Arabic-Indic digit seven.
        ("8", "٨"),  # U+0668 Arabic-Indic digit eight.
        ("9", "٩"),  # U+0669 Arabic-Indic digit nine.
    )

    ignoretests = {
        "all": ["acronyms", "simplecaps", "startcaps"],
    }

    @classmethod
    def punctranslate(cls, text):
        text = super().punctranslate(text)
        return reverse_quotes(text)
