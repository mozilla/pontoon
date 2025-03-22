#
# Copyright 2010 Zuza Software Foundation
#
# This file is part of Virtaal.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Py2exe can't find stuff that we import dynamically, so we have this file
just for the sake of the Windows installer to easily pick up all the stuff that
we need and ensure they make it into the installer.
"""

import contextlib

from . import (
    catkeys,
    csvl10n,
    mo,
    omegat,
    po,
    qm,
    qph,
    tbx,
    tmx,
    ts2,
    utx,
    wordfast,
    xliff,
)

with contextlib.suppress(ImportError):
    from . import trados

__all__ = [
    "catkeys",
    "csvl10n",
    "mo",
    "omegat",
    "po",
    "qm",
    "qph",
    "tbx",
    "tmx",
    "trados",
    "ts2",
    "utx",
    "wordfast",
    "xliff",
]
