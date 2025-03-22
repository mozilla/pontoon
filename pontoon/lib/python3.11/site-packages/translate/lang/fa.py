#
# Copyright 2007, 2010 Zuza Software Foundation
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
This module represents the Persian language.

.. seealso:: :wp:`Persian_language`
"""

import re

from translate.lang import common


def guillemets(text):
    def convertquotation(match):
        prefix = match.group(1)
        # Let's see that we didn't perhaps match an XML tag property like
        # <a href="something">
        if prefix == "=":
            return match.group(0)
        return f"{prefix}«{match.group(2)}»"

    # Check that there is an even number of double quotes, otherwise it is
    # probably not safe to convert them.
    if text.count('"') % 2 == 0:
        text = re.sub('(.|^)"([^"]+)"', convertquotation, text)
    singlecount = text.count("'")
    if singlecount:
        if singlecount == text.count("`"):
            text = re.sub("(.|^)`([^']+)'", convertquotation, text)
        elif singlecount % 2 == 0:
            text = re.sub("(.|^)'([^']+)'", convertquotation, text)
    return re.sub("(.|^)“([^”]+)”", convertquotation, text)


class fa(common.Common):
    """This class represents Persian."""

    listseperator = "، "

    puncdict = {
        ",": "،",
        ";": "؛",
        "?": "؟",
        # This causes problems with variables, so commented out for now:
        # "%": "٪",
    }

    numbertuple = (
        # It seems that Persian uses both Arabic-Indic and Extended
        # Arabic-Indic digits.
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
        ("0", "۰"),  # U+06F0 Extended Arabic-Indic digit zero.
        ("1", "۱"),  # U+06F1 Extended Arabic-Indic digit one.
        ("2", "۲"),  # U+06F2 Extended Arabic-Indic digit two.
        ("3", "۳"),  # U+06F3 Extended Arabic-Indic digit three.
        ("4", "۴"),  # U+06F4 Extended Arabic-Indic digit four.
        ("5", "۵"),  # U+06F5 Extended Arabic-Indic digit five.
        ("6", "۶"),  # U+06F6 Extended Arabic-Indic digit six.
        ("7", "۷"),  # U+06F7 Extended Arabic-Indic digit seven.
        ("8", "۸"),  # U+06F8 Extended Arabic-Indic digit eight.
        ("9", "۹"),  # U+06F9 Extended Arabic-Indic digit nine.
    )

    ignoretests = {
        "all": ["simplecaps", "startcaps"],
    }
    # TODO: check persian numerics
    # TODO: zwj and zwnj?

    @classmethod
    def punctranslate(cls, text):
        """Implement "French" quotation marks."""
        text = super().punctranslate(text)
        return guillemets(text)
