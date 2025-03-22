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

"""This module provides functionality to work with zip files."""

# Perhaps all methods should work with a wildcard to limit searches in some
# way (examples: *.po, base.xlf, pootle-terminology.tbx)

# TODO: consider also providing directories as we currently provide files

from io import BytesIO
from zipfile import ZipFile

from translate.storage import directory, factory


class ZIPFile(directory.Directory):
    """This class represents a ZIP file like a directory."""

    def __init__(self, filename=None):
        self.filename = filename
        self.filedata = []
        self.archive = None

    def unit_iter(self):
        """Iterator over all the units in all the files in this zip file."""
        for dirname, filename in self.file_iter():
            strfile = BytesIO(self.archive.read(f"{dirname}/{filename}"))
            strfile.filename = filename
            store = factory.getobject(strfile)
            # TODO: don't regenerate all the storage objects
            yield from store.unit_iter()

    def scanfiles(self):
        """Populate the internal file data."""
        self.filedata = []
        self.archive = ZipFile(self.filename)
        for completename in self.archive.namelist():
            if "/" in completename:
                dir, name = completename.rsplit("/", 1)
            else:
                dir = ""
                name = completename
            self.filedata.append((dir, name))

    def close(self):
        if self.archive is not None:
            self.archive.close()
            self.archive = None
