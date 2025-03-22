#
# Copyright 2008, 2011 Zuza Software Foundation
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

# Original Author: Dan Schafer <dschafer@mozilla.com>
# Date: 10 Jun 2008

"""
A class to manage Mozilla .lang files.

See https://github.com/mozilla-l10n/langchecker/wiki/.lang-files-format for
specifications on the format.
"""

from translate.storage import base, txt


def strip_ok(string):
    tmpstring = string.rstrip()
    if tmpstring.endswith(("{ok}", "{OK}")):
        return tmpstring[:-4].rstrip()
    return string


class LangUnit(base.TranslationUnit):
    """This is just a normal unit with a weird string output."""

    def __init__(self, source=None):
        self.locations = []
        self.eol = "\n"
        self.rawtarget = None
        super().__init__(source)

    def __str__(self):
        target = self.target if self.istranslated() else self.source
        if self.source == self.target:
            target = self.target + " {ok}"
        if (
            self.rawtarget is not None
            and self.target == strip_ok(self.rawtarget)
            and len(self.target) != len(strip_ok(self.rawtarget))
        ):
            target = self.rawtarget
        if self.getnotes():
            notes = (self.eol).join(
                [
                    (f"#{note}" if note.startswith("#") else f"# {note}")
                    for note in self.getnotes("developer").split("\n")
                ]
            )
            return f"{notes}{self.eol};{self.source}{self.eol}{target}"
        return f";{self.source}{self.eol}{target}"

    def getlocations(self):
        return self.locations

    def addlocation(self, location):
        self.locations.append(location)


class LangStore(txt.TxtFile):
    """We extend TxtFile, since that has a lot of useful stuff for encoding."""

    UnitClass = LangUnit

    Name = "Mozilla .lang"
    Extensions = ["lang"]

    def __init__(self, inputfile=None, mark_active=False, **kwargs):
        self.is_active = False
        self.mark_active = mark_active
        self._headers = []
        self.eol = "\n"
        self.location_root = getattr(inputfile, "location_root", "")
        super().__init__(inputfile, **kwargs)

    def parse(self, lines):
        source_unit = None
        comment = ""
        if not isinstance(lines, list):
            lines = lines.split(b"\n")

        for lineoffset, line in enumerate(lines):
            if line.endswith(b"\r"):
                self.eol = "\r\n"
            line = line.decode(self.encoding).rstrip("\n").rstrip("\r")

            if lineoffset == 0 and line == "## active ##":
                self.is_active = True
                continue

            header_meta_data = (
                line.startswith("## ")
                and not line.startswith("## TAG")
                and not line.startswith("## MAX_LENGTH")
            )
            if header_meta_data:
                self._headers.append(line)
                continue

            if len(line) == 0 and not source_unit:
                if len(self.units) == 0:
                    self._headers.append(line)  # Append blank lines to header
                # else skip blank lines
                continue

            if source_unit:
                # If we have a source_unit get the target
                source_unit.rawtarget = line
                if line != source_unit.source:
                    source_unit.target = strip_ok(line)
                else:
                    source_unit.target = ""
                source_unit = None
                continue

            is_comment = line.startswith("#") and (
                not line.startswith("##")
                or line.startswith(("## TAG", "## MAX_LENGTH"))
            )
            if is_comment:
                # Read comments, *including* meta tags (e.g. '## TAG')
                comment += line[1:].strip() + "\n"

            if line.startswith(";"):
                source_unit = self.addsourceunit(line[1:])
                source_unit.eol = self.eol
                source_unit.addlocation(
                    "%s:%d" % (self.filename[len(self.location_root) :], lineoffset + 1)
                )
                if comment is not None:
                    source_unit.addnote(comment[:-1], "developer")
                    comment = ""

    def serialize(self, out):
        eol = self.eol.encode("utf-8")
        if self.is_active or self.mark_active:
            out.write(b"## active ##")
            out.write(eol)
        for header in self._headers:
            out.write(str(header).encode("utf-8"))
            out.write(eol)
        for unit in self.units:
            out.write(str(unit).encode("utf-8"))
            out.write(eol * 3)

    def getlangheaders(self):
        return self._headers
