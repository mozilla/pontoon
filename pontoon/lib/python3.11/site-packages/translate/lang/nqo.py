#
# Copyright 2013 Zuza Software Foundation
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
This module represents the N'Ko language.

.. seealso:: :wp:`N'Ko_language`
"""

import re

from translate.lang import common


def reverse_quotes(text):
    def convertquotation(match):
        return f"”{match.group(1)}“"

    return re.sub("“([^”]+)”", convertquotation, text)


class nqo(common.Common):
    """This class represents N'Ko."""

    listseperator = "߸ "

    puncdict = {
        ",": "߸",
        ";": "؛",
        "?": "؟",
        "!": "߹",
    }

    ignoretests = {
        "all": ["acronyms", "simplecaps", "startcaps"],
    }

    @classmethod
    def punctranslate(cls, text):
        text = super().punctranslate(text)
        return reverse_quotes(text)
