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
This module represents the Urdu language.

.. seealso:: :wp:`Urdu_language`
"""

from translate.lang import common


class ur(common.Common):
    """This class represents Urdu."""

    listseperator = "، "

    puncdict = {
        ".": "۔",
        ",": "،",
        ";": "؛",
        "?": "؟",
        # This causes problems with variables, so commented out for now:
        # "%": "٪",
    }

    ignoretests = {
        "all": ["simplecaps", "startcaps"],
    }
