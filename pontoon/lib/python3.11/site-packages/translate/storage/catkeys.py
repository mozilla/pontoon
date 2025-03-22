#
# Copyright 2010 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
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
Manage the Haiku catkeys translation format.

The Haiku catkeys format is the translation format used for localisation of
the `Haiku <http://www.haiku-os.org/>`_ operating system.

It is a bilingual base class derived format with :class:`CatkeysFile` and
:class:`CatkeysUnit` providing file and unit level access.  The file format is
described here:
http://www.haiku-os.org/blog/pulkomandy/2009-09-24_haiku_locale_kit_translator_handbook

Implementation
    The implementation covers the full requirements of a catkeys file. The
    files are simple Tab Separated Value (TSV) files that can be read
    by Microsoft Excel and other spreadsheet programs. They use the .txt
    extension which does make it more difficult to automatically identify
    such files.

    The dialect of the TSV files is specified by :class:`CatkeysDialect`.

Encoding
    The files are UTF-8 encoded.

Header
    :class:`CatkeysHeader` provides header management support.

Escaping
    catkeys seem to escape things like in C++ (strings are just extracted from
    the source code unchanged, it seems.

    Functions allow for :func:`._escape` and :func:`._unescape`.
"""

import csv

from translate.lang import data
from translate.storage import base

FIELDNAMES_HEADER = ["version", "language", "mimetype", "checksum"]
"""Field names for the catkeys header"""

FIELDNAMES = ["source", "context", "comment", "target"]
"""Field names for a catkeys TU"""

FIELDNAMES_HEADER_DEFAULTS = {
    "version": "1",
    "language": "",
    "mimetype": "",
    "checksum": "",
}
"""Default or minimum header entries for a catkeys file"""

_unescape_map = {"\\r": "\r", "\\t": "\t", "\\n": "\n", "\\\\": "\\"}
_escape_map = {value: key for (key, value) in _unescape_map.items()}
# We don't yet do escaping correctly, just for lack of time to do it.  The
# current implementation is just based on something simple that will work with
# investaged files.  The only escapes found were "\n", "\t", "\\n"


def _escape(string):
    if string:
        string = string.replace(r"\n", r"\\n").replace("\n", "\\n").replace("\t", "\\t")
    return string


def _unescape(string):
    if string:
        string = string.replace("\\n", "\n").replace("\\t", "\t").replace(r"\n", r"\\n")
    return string


class CatkeysDialect(csv.Dialect):
    """Describe the properties of a catkeys generated TAB-delimited file."""

    delimiter = "\t"
    lineterminator = "\n"
    quoting = csv.QUOTE_NONE


csv.register_dialect("catkeys", CatkeysDialect)


class CatkeysHeader:
    """A catkeys translation memory header."""

    def __init__(self, header=None):
        self._header_dict = {}
        if not header:
            self._header_dict = self._create_default_header()
        elif isinstance(header, dict):
            for key in FIELDNAMES_HEADER:
                value = header.get(key, "")
                if value is None:
                    value = ""
                self._header_dict[key] = value

    @staticmethod
    def _create_default_header():
        """Create a default catkeys header."""
        return FIELDNAMES_HEADER_DEFAULTS.copy()

    def settargetlanguage(self, newlang):
        """Set a human readable target language."""
        if not newlang or newlang not in data.languages:
            return
        # XXX assumption about the current structure of the languages dict in data
        self._header_dict["language"] = data.languages[newlang][0].lower()

    targetlanguage = property(None, settargetlanguage)

    def setchecksum(self, checksum):
        """Set the checksum for the file."""
        if not checksum:
            return
        self._header_dict["checksum"] = str(checksum)


class CatkeysUnit(base.TranslationUnit):
    """A catkeys translation memory unit."""

    def __init__(self, source=None):
        self._dict = {}
        if source:
            self.source = source
        super().__init__(source)

    def getdict(self):
        """Get the dictionary of values for a catkeys line."""
        return self._dict

    def setdict(self, newdict):
        """
        Set the dictionary of values for a catkeys line.

        :param newdict: a new dictionary with catkeys line elements
        :type newdict: Dict
        """
        # Process the input values
        self._dict = {}
        for key in FIELDNAMES:
            value = newdict.get(key, "")
            if value is None:
                value = ""
            self._dict[key] = value

    dict = property(getdict, setdict)

    def _get_source_or_target(self, key):
        if self._dict.get(key) is None:
            return None
        if self._dict[key]:
            return _unescape(self._dict[key])
        return ""

    def _set_source_or_target(self, key, newvalue):
        if newvalue is None:
            self._dict[key] = None
        newvalue = _escape(newvalue)
        if key not in self._dict or newvalue != self._dict[key]:
            self._dict[key] = newvalue

    @property
    def source(self):
        return self._get_source_or_target("source")

    @source.setter
    def source(self, source):
        self._rich_source = None
        self._set_source_or_target("source", source)

    @property
    def target(self):
        return self._get_source_or_target("target")

    @target.setter
    def target(self, target):
        self._rich_target = None
        self._set_source_or_target("target", target)

    def getnotes(self, origin=None):
        if not origin or origin in {"programmer", "developer", "source code"}:
            return self._dict.get("comment", "")
        return ""

    def getcontext(self):
        return self._dict.get("context", "")

    def setcontext(self, context):
        self._dict["context"] = context

    def getid(self):
        context = self.getcontext()
        notes = self.getnotes()
        id = self.source
        if notes:
            id = f"{notes}\04{id}"
        if context:
            id = f"{context}\04{id}"
        return id

    def markfuzzy(self, present=True):
        if present:
            self.target = ""

    def settargetlang(self, newlang):
        self._dict["target-lang"] = newlang

    targetlang = property(None, settargetlang)

    def __str__(self):
        return str(self._dict)

    def istranslated(self):
        if not self._dict.get("source"):
            return False
        return bool(self._dict.get("target"))

    def merge(self, otherunit, overwrite=False, comments=True, authoritative=False):
        """Do basic format agnostic merging."""
        # We can't go fuzzy, so just do nothing
        if (
            self.source != otherunit.source
            or self.getcontext() != otherunit.getcontext()
            or otherunit.isfuzzy()
        ):
            return
        if not self.istranslated() or overwrite:
            self.rich_target = otherunit.rich_target


class CatkeysFile(base.TranslationStore):
    """A catkeys translation memory file."""

    Name = "Haiku catkeys file"
    Mimetypes = ["application/x-catkeys"]
    Extensions = ["catkeys"]
    UnitClass = CatkeysUnit

    def __init__(self, inputfile=None, **kwargs):
        """Construct a catkeys store, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = ""
        self.header = CatkeysHeader()
        if inputfile is not None:
            self.parse(inputfile)

    def settargetlanguage(self, newlang):
        self.header.settargetlanguage(newlang)

    def parse(self, input):
        """Parse the given file or file source string."""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            tmsrc = input.read()
            input.close()
            input = tmsrc
        input = input.decode(self.encoding)
        reader = csv.DictReader(
            input.split("\n"), fieldnames=FIELDNAMES, dialect="catkeys"
        )
        for idx, line in enumerate(reader):
            if idx == 0:
                header = dict(zip(FIELDNAMES_HEADER, [line[key] for key in FIELDNAMES]))
                self.header = CatkeysHeader(header)
                continue
            newunit = CatkeysUnit()
            newunit.dict = line
            self.addunit(newunit)

    def serialize(self, out):
        output = csv.StringIO()
        writer = csv.DictWriter(output, FIELDNAMES, dialect="catkeys")
        # Calculate/update fingerprint
        self.header.setchecksum(self._compute_fingerprint())
        # No real headers, the first line contains metadata
        writer.writerow(
            dict(
                zip(
                    FIELDNAMES,
                    [self.header._header_dict[key] for key in FIELDNAMES_HEADER],
                )
            )
        )
        for unit in self.units:
            writer.writerow(unit.dict)
        out.write(output.getvalue().encode(self.encoding))

    def _compute_fingerprint(self):
        """Compute the current hash key in the header for the current state of the store."""

        def hashfun(string, startValue):
            """
            This function is on CatKey::HashFun(). In this implementation C integer overflow is emulated.
            https://github.com/haiku/haiku/blob/b65adbdfbc322bb7d86d74049389c688e9962f15/src/kits/locale/HashMapCatalog.cpp#L93.
            """
            h = startValue
            array = string.encode("utf-8")

            for byte in array:
                if byte > 127:
                    byte -= 256
                h = 5 * h + byte
                h &= 0xFFFFFFFF

            # Add 1
            h = 5 * h + 1
            h &= 0xFFFFFFFF

            return h

        fingerprint = 0
        for unit in self.units:
            stringhash = hashfun(unit.source, 0)
            stringhash &= 0xFFFFFFFF
            stringhash = hashfun(unit.getcontext(), stringhash)
            stringhash &= 0xFFFFFFFF
            stringhash = hashfun(unit.getnotes(), stringhash)
            stringhash &= 0xFFFFFFFF
            fingerprint += stringhash
            fingerprint &= 0xFFFFFFFF

        return fingerprint
