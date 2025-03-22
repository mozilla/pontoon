#
# Copyright 2002-2006 Zuza Software Foundation
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
classes that hold units of comma-separated values (.csv) files (csvunit)
or entire files (csvfile) for use with localisation.
"""

from __future__ import annotations

import csv

from translate.storage import base


class DefaultDialect(csv.excel):
    skipinitialspace = True
    quoting = csv.QUOTE_ALL
    escapechar = "\\"


csv.register_dialect("default", DefaultDialect)


class csvunit(base.TranslationUnit):
    spreadsheetescapes = [("+", "\\+"), ("-", "\\-"), ("=", "\\="), ("'", "\\'")]

    def __init__(self, source=None):
        super().__init__(source)
        self.location = ""
        self.source = source or ""
        self.target = ""
        self.id = ""
        self.fuzzy = "False"
        self.developer_comments = ""
        self.translator_comments = ""
        self.context = ""

    def getid(self):
        if self.id:
            return self.id

        result = self.source
        context = self.context
        if context:
            result = f"{context}\04{result}"

        return result

    def setid(self, value):
        self.id = value

    def getlocations(self):
        # FIXME: do we need to support more than one location
        return [self.location]

    def addlocation(self, location):
        self.location = location

    def getcontext(self):
        return self.context

    def setcontext(self, value):
        self.context = value

    def getnotes(self, origin=None):
        if origin is None:
            result = self.translator_comments
            if self.developer_comments:
                if result:
                    result += "\n" + self.developer_comments
                else:
                    result = self.developer_comments
            return result
        if origin == "translator":
            return self.translator_comments
        if origin in {"programmer", "developer", "source code"}:
            return self.developer_comments
        raise ValueError("Comment type not valid")

    def addnote(self, text, origin=None, position="append"):
        if origin in {"programmer", "developer", "source code"}:
            if position == "append" and self.developer_comments:
                self.developer_comments += "\n" + text
            elif position == "prepend" and self.developer_comments:
                self.developer_comments = text + "\n" + self.developer_comments
            else:
                self.developer_comments = text
        elif position == "append" and self.translator_comments:
            self.translator_comments += "\n" + text
        elif position == "prepend" and self.translator_comments:
            self.translator_comments = self.translator_comments + "\n" + text
        else:
            self.translator_comments = text

    def removenotes(self, origin=None):
        self.translator_comments = ""

    def isfuzzy(self):
        return self.fuzzy.lower() in {"1", "x", "true", "yes", "fuzzy"}

    def markfuzzy(self, value=True):
        if value:
            self.fuzzy = "True"
        else:
            self.fuzzy = "False"

    def match_header(self):
        """See if unit might be a header."""
        some_value = False
        for key, value in self.todict().items():
            if value:
                some_value = True
            if key.lower() != "fuzzy" and value and key.lower() != value.lower():
                return False
        return some_value

    def add_spreadsheet_escapes(self, source, target):
        """Add common spreadsheet escapes to two strings."""
        for unescaped, escaped in self.spreadsheetescapes:
            if source.startswith(unescaped):
                source = source.replace(unescaped, escaped, 1)
            if target.startswith(unescaped):
                target = target.replace(unescaped, escaped, 1)
        return source, target

    def remove_spreadsheet_escapes(self, source, target):
        """Remove common spreadsheet escapes from two strings."""
        for unescaped, escaped in self.spreadsheetescapes:
            if source.startswith(escaped):
                source = source.replace(escaped, unescaped, 1)
            if target.startswith(escaped):
                target = target.replace(escaped, unescaped, 1)
        return source, target

    def fromdict(self, cedict, encoding="utf-8"):
        for key, value in cedict.items():
            rkey = fieldname_map.get(key, key)
            if value is None or key is None or key == EXTRA_KEY:
                continue
            if rkey == "id":
                self.id = value
            elif rkey == "source":
                self.source = value
            elif rkey == "target":
                self.target = value
            elif rkey == "location":
                self.location = value
            elif rkey == "fuzzy":
                self.fuzzy = value
            elif rkey == "context":
                self.context = value
            elif rkey == "translator_comments":
                self.translator_comments = value
            elif rkey == "developer_comments":
                self.developer_comments = value

        # self.source, self.target = self.remove_spreadsheet_escapes(self.source, self.target)

    def todict(self, **kwargs):
        # FIXME: use apis?
        # source, target = self.add_spreadsheet_escapes(self.source, self.target)
        return {
            "location": self.location,
            "source": self.source,
            "target": self.target,
            "id": self.id,
            "fuzzy": str(self.fuzzy),
            "context": self.context,
            "translator_comments": self.translator_comments,
            "developer_comments": self.developer_comments,
        }

    def __str__(self):
        return str(self.todict())


fieldname_map = {
    "original": "source",
    "untranslated": "source",
    "translated": "target",
    "translation": "target",
    "identified": "id",
    "key": "id",
    "label": "id",
    "translator comments": "translator_comments",
    "notes": "translator_comments",
    "developer comments": "developer_comments",
    "state": "fuzzy",
}


EXTRA_KEY = "__CSVL10N__EXTRA__"


def try_dialects(inputfile, fieldnames, dialect):
    # FIXME: does it verify at all if we don't actually step through the file?
    try:
        inputfile.seek(0)
        return csv.DictReader(
            inputfile, fieldnames=fieldnames, dialect=dialect, restkey=EXTRA_KEY
        )
    except csv.Error:
        try:
            inputfile.seek(0)
            return csv.DictReader(
                inputfile, fieldnames=fieldnames, dialect="default", restkey=EXTRA_KEY
            )
        except csv.Error:
            inputfile.seek(0)
            return csv.DictReader(
                inputfile, fieldnames=fieldnames, dialect="excel", restkey=EXTRA_KEY
            )


def valid_fieldnames(fieldnames):
    """
    Check if fieldnames are valid, that is at least one field is identified
    as the source.
    """
    return any(
        fieldname == "source" or fieldname_map.get(fieldname) == "source"
        for fieldname in fieldnames
    )


def detect_header(inputfile, dialect, fieldnames):
    """Test if file has a header or not, also returns number of columns in first row."""
    try:
        reader = csv.reader(inputfile, dialect)
    except csv.Error:
        try:
            inputfile.seek(0)
            reader = csv.reader(inputfile, "default")
        except csv.Error:
            inputfile.seek(0)
            reader = csv.reader(inputfile, "excel")

    header = next(reader)
    columncount = max(len(header), 3)
    if valid_fieldnames(header):
        return header
    return fieldnames[:columncount]


class csvfile(base.TranslationStore):
    """
    This class represents a .csv file with various lines.  The default
    format contains three columns: location, source, target.
    """

    UnitClass = csvunit
    Name = "Comma Separated Value"
    Mimetypes = ["text/comma-separated-values", "text/csv"]
    Extensions = ["csv"]

    def __init__(self, inputfile=None, fieldnames=None, encoding="auto"):
        super().__init__(encoding=encoding)
        if not fieldnames:
            self.fieldnames = [
                "location",
                "source",
                "target",
                "id",
                "fuzzy",
                "context",
                "translator_comments",
                "developer_comments",
            ]
        else:
            self.fieldnames = fieldnames
        self.filename = getattr(inputfile, "name", "")
        self.dialect = "default"
        if inputfile is not None:
            csvsrc = inputfile.read()
            inputfile.close()
            self.parse(csvsrc)

    def parse(
        self, csvsrc, sample_length: int | None = 1024, *, dialect: None | str = None
    ):
        if self._encoding == "auto":
            text, encoding = self.detect_encoding(
                csvsrc, default_encodings=["utf-8", "utf-16"]
            )
            if text is None:
                raise ValueError("Could not detect enconding!")
            self.encoding = encoding or "utf-8"
        else:
            text = csvsrc.decode(self.encoding)

        sniffer = csv.Sniffer()
        sample = text[:sample_length] if sample_length else text

        if dialect is not None:
            self.dialect = dialect
        else:
            try:
                self.dialect = sniffer.sniff(sample)
                if self.dialect.quoting == csv.QUOTE_MINIMAL:
                    # HACKISH: most probably a default, not real detection
                    self.dialect.quoting = csv.QUOTE_ALL
                    self.dialect.doublequote = True
            except csv.Error:
                self.dialect = "default"

        inputfile = csv.StringIO(text)
        try:
            fieldnames = detect_header(inputfile, self.dialect, self.fieldnames)
            self.fieldnames = fieldnames
        except csv.Error:
            pass

        inputfile.seek(0)
        reader = try_dialects(inputfile, self.fieldnames, self.dialect)

        first_row = True
        for row in reader:
            newce = self.UnitClass()
            newce.fromdict(row)
            if not first_row or not newce.match_header():
                self.addunit(newce)
            first_row = False

    def serialize(self, out):
        """Write to file."""
        source = self.getoutput()
        if isinstance(source, str):
            # Python 3
            out.write(source.encode(self.encoding))
        else:
            out.write(source)

    def getoutput(self):
        output = csv.StringIO()
        writer = csv.DictWriter(
            output, self.fieldnames, extrasaction="ignore", dialect=self.dialect
        )
        writer.writeheader()
        for ce in self.units:
            writer.writerow(ce.todict())
        return output.getvalue()
