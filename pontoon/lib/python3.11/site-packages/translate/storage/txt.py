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

"""
This class implements the functionality for handling plain text files, or
similar wiki type files.

Supported formats are
  - Plain text
  - dokuwiki
  - MediaWiki
"""

import re

from translate.storage import base

dokuwiki = [
    (
        "Dokuwiki heading",
        re.compile(r"( ?={2,6}[\s]*)(.+)"),
        re.compile(r"([\s]*={2,6}[\s]*)$"),
    ),
    ("Dokuwiki bullet", re.compile(r"([\s]{2,}\*[\s]*)(.+)"), re.compile(r"[\s]+$")),
    (
        "Dokuwiki numbered item",
        re.compile(r"([\s]{2,}-[\s]*)(.+)"),
        re.compile(r"[\s]+$"),
    ),
]

mediawiki = [
    (
        "MediaWiki heading",
        re.compile(r"(={1,5}[\s]*)(.+)"),
        re.compile(r"([\s]*={1,5}[\s]*)$"),
    ),
    ("MediaWiki bullet", re.compile(r"(\*+[\s]*)(.+)"), re.compile(r"[\s]+$")),
    ("MediaWiki numbered item", re.compile(r"(#+[\s]*)(.+)"), re.compile(r"[\s]+$")),
]

flavours = {
    "dokuwiki": dokuwiki,
    "mediawiki": mediawiki,
    None: [],
    "plain": [],
}


class TxtUnit(base.TranslationUnit):
    """This class represents a block of text from a text file."""

    def __init__(self, source="", **kwargs):
        """Construct the txtunit."""
        super().__init__(source)
        # Note that source and target are equivalent for monolingual units.
        self.source = source
        self.pretext = ""
        self.posttext = ""
        self.location = []

    def __str__(self):
        """Convert a txt unit to a string."""
        return f"{self.pretext}{self.source}{self.posttext}"

    @property
    def target(self):
        """Gets the unquoted target string."""
        return self.source

    @target.setter
    def target(self, target):
        """Sets the definition to the quoted value of target."""
        self._rich_target = None
        self.source = target

    def addlocation(self, location):
        self.location.append(location)

    def getlocations(self):
        return self.location


class TxtFile(base.TranslationStore):
    """This class represents a text file, made up of txtunits."""

    UnitClass = TxtUnit

    def __init__(self, inputfile=None, flavour=None, no_segmentation=False, **kwargs):
        super().__init__(**kwargs)
        self.filename = getattr(inputfile, "name", "")
        self.flavour = flavours.get(flavour, [])
        self.no_segmentation = no_segmentation
        if inputfile is not None:
            txtsrc = inputfile.readlines()
            self.parse(txtsrc)

    def parse(self, lines):
        """Read in text lines and create txtunits from the blocks of text."""
        if self.no_segmentation:
            self.addsourceunit("".join(line.decode(self.encoding) for line in lines))
            return
        block = []
        current_line = 0
        pretext = ""
        posttext = ""
        if not isinstance(lines, list):
            lines = lines.split(b"\n")
        for linenum, line in enumerate(lines):
            current_line = linenum + 1
            line = line.decode(self.encoding).rstrip("\r\n")
            for _rule, prere, postre in self.flavour:
                match = prere.match(line)
                if match:
                    pretext, source = match.groups()
                    postmatch = postre.search(source)
                    if postmatch:
                        posttext = postmatch.group()
                        source = source[: postmatch.start()]
                    block.append(source)
                    isbreak = True
                    break
            else:
                isbreak = not line.strip()
            if isbreak and block:
                unit = self.addsourceunit("\n".join(block))
                unit.addlocation("%s:%d" % (self.filename, current_line))
                unit.pretext = pretext
                unit.posttext = posttext
                pretext = ""
                posttext = ""
                block = []
            elif not isbreak:
                block.append(line)
        if block:
            unit = self.addsourceunit("\n".join(block))
            unit.addlocation("%s:%d" % (self.filename, current_line))

    def serialize(self, out):
        for idx, unit in enumerate(self.units):
            if idx > 0:
                out.write(b"\n\n")
            out.write(str(unit).encode(self.encoding))
