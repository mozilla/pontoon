#
# Copyright 2010 Zuza Software Foundation
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
This module represents the Uyghur language.

.. seealso:: :wp:`Uyghur_language`
"""

from translate.lang import common


class ug(common.Common):
    """This class represents Uyghur."""

    listseperator = "، "

    puncdict = {
        ",": "،",
        ";": "؛",
        "?": "؟",
    }

    ignoretests = {
        "all": ["acronyms", "simplecaps", "startcaps"],
    }
