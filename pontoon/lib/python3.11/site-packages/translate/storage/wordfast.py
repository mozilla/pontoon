#
# Copyright 2007-2010 Zuza Software Foundation
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
Manage the Wordfast Translation Memory format.

Wordfast TM format is the Translation Memory format used by the
`Wordfast <http://www.wordfast.net/>`_ computer aided translation tool.

It is a bilingual base class derived format with :class:`WordfastTMFile`
and :class:`WordfastUnit` providing file and unit level access.

Wordfast is a computer aided translation tool.  It is an application
built on top of Microsoft Word and is implemented as a rather
sophisticated set of macros.  Understanding that helps us understand
many of the seemingly strange choices around this format including:
encoding, escaping and file naming.

Implementation
    The implementation covers the full requirements of a Wordfast TM file.
    The files are simple Tab Separated Value (TSV) files that can be read
    by Microsoft Excel and other spreadsheet programs.  They use the .txt
    extension which does make it more difficult to automatically identify
    such files.

    The dialect of the TSV files is specified by :class:`WordfastDialect`.

Encoding
    The files are UTF-16 or ISO-8859-1 (Latin1) encoded.  These choices
    are most likely because Microsoft Word is the base editing tool for
    Wordfast.

    The format is tab separated so we are able to detect UTF-16 vs Latin-1
    by searching for the occurance of a UTF-16 tab character and then
    continuing with the parsing.

Timestamps
    :class:`WordfastTime` allows for the correct management of the Wordfast
    YYYYMMDD~HHMMSS timestamps.  However, timestamps on individual units are
    not updated when edited.

Header
    :class:`WordfastHeader` provides header management support.  The header
    functionality is fully implemented through observing the behaviour of the
    files in real use cases, input from the Wordfast programmers and
    public documentation.

Escaping
    Wordfast TM implements a form of escaping that covers two aspects:

    1. Placeable: bold, formating, etc.  These are left as is and ignored.  It
       is up to the editor and future placeable implementation to manage these.

    2. Escapes: items that may confuse Excel or translators are escaped as
       ``&'XX;``. These are fully implemented and are converted to and from
       Unicode.  By observing behaviour and reading documentation we where able
       to observe all possible escapes. Unfortunately the escaping differs
       slightly between Windows and Mac version.  This might cause errors in
       future.  Functions allow for ``<_wf_to_char>`` and back to Wordfast
       escape (``<_char_to_wf>``).

Extended Attributes
    The last 4 columns allow users to define and manage extended attributes.
    These are left as is and are not directly managed byour implemenation.
"""

import csv
import time

from translate.storage import base

WF_TIMEFORMAT = "%Y%m%d~%H%M%S"
"""Time format used by Wordfast"""

WF_FIELDNAMES_HEADER = [
    "date",
    "userlist",
    "tucount",
    "src-lang",
    "version",
    "target-lang",
    "license",
    "attr1list",
    "attr2list",
    "attr3list",
    "attr4list",
    "attr5list",
]
"""Field names for the Wordfast header"""

WF_FIELDNAMES = [
    "date",
    "user",
    "reuse",
    "src-lang",
    "source",
    "target-lang",
    "target",
    "attr1",
    "attr2",
    "attr3",
    "attr4",
    "attr5",
]
"""Field names for a Wordfast TU"""

WF_FIELDNAMES_HEADER_DEFAULTS = {
    "date": "%19000101~121212",
    "userlist": "%User ID,TT,TT Translate-Toolkit",
    "tucount": "%TU=00000001",
    "src-lang": "%EN-US",
    "version": "%Wordfast TM v.5.51w9/00",
    "target-lang": "",
    "license": "%---00000001",
    "attr1list": "",
    "attr2list": "",
    "attr3list": "",
    "attr4list": "",
    "attr5list": "",
}
"""Default or minimum header entries for a Wordfast file"""

# TODO Needs validation.  The following need to be checked against a WF TM file
# to ensure that the correct Unicode values have been chosen for the characters.
# For now these look correct and have been taken from Windows CP1252 and
# Macintosh code points found for the respective character sets on Linux.
WF_ESCAPE_MAP = (
    ("&'26;", "\u0026"),  # & - Ampersand (must be first to prevent
    #     escaping of escapes)
    ("&'82;", "\u201a"),  # ‚ - Single low-9 quotation mark
    ("&'85;", "\u2026"),  # … - Elippsis
    ("&'91;", "\u2018"),  # ‘ - left single quotation mark
    ("&'92;", "\u2019"),  # ’ - right single quotation mark
    ("&'93;", "\u201c"),  # “ - left double quotation mark
    ("&'94;", "\u201d"),  # ” - right double quotation mark
    ("&'96;", "\u2013"),  # – - en dash (validate)
    ("&'97;", "\u2014"),  # — - em dash (validate)
    ("&'99;", "\u2122"),  # ™ - Trade mark
    # Windows only
    ("&'A0;", "\u00a0"),  #   - Non breaking space
    ("&'A9;", "\u00a9"),  # © - Copyright
    ("&'AE;", "\u00ae"),  # ® - Registered
    ("&'BC;", "\u00bc"),  # ¼
    ("&'BD;", "\u00bd"),  # ½
    ("&'BE;", "\u00be"),  # ¾
    # Mac only
    ("&'A8;", "\u00ae"),  # ® - Registered
    ("&'AA;", "\u2122"),  # ™ - Trade mark
    ("&'C7;", "\u00ab"),  # « - Left-pointing double angle quotation mark
    ("&'C8;", "\u00bb"),  # » - Right-pointing double angle quotation mark
    ("&'C9;", "\u2026"),  # … - Horizontal Elippsis
    ("&'CA;", "\u00a0"),  #   - Non breaking space
    ("&'D0;", "\u2013"),  # – - en dash (validate)
    ("&'D1;", "\u2014"),  # — - em dash (validate)
    ("&'D2;", "\u201c"),  # “ - left double quotation mark
    ("&'D3;", "\u201d"),  # ” - right double quotation mark
    ("&'D4;", "\u2018"),  # ‘ - left single quotation mark
    ("&'D5;", "\u2019"),  # ’ - right single quotation mark
    ("&'E2;", "\u201a"),  # ‚ - Single low-9 quotation mark
    ("&'E3;", "\u201e"),  # „ - Double low-9 quotation mark
    # Other markers
    # Soft-break - XXX creates a problem with roundtripping could
    # also be represented by \u2028
    # ("&'B;", "\n"),
)
"""Mapping of Wordfast &'XX; escapes to correct Unicode characters"""

TAB_UTF16 = b"\x00\x09"
"""The tab \\t character as it would appear in UTF-16 encoding"""


def _char_to_wf(string):
    r"""
    Char -> Wordfast &'XX; escapes.

    Full roundtripping is not possible because of the escaping of
    NEWLINE \\n and TAB \\t
    """
    # FIXME there is no platform check to ensure that we use Mac encodings
    # when running on a Mac
    if string:
        for code, char in WF_ESCAPE_MAP:
            string = string.replace(char, code)
        string = string.replace("\n", "\\n").replace("\t", "\\t")
    return string


def _wf_to_char(string):
    """Wordfast &'XX; escapes -> Char."""
    if string:
        for code, char in WF_ESCAPE_MAP:
            string = string.replace(code, char)
        string = string.replace("\\n", "\n").replace("\\t", "\t")
    return string


class WordfastDialect(csv.Dialect):
    """Describe the properties of a Wordfast generated TAB-delimited file."""

    delimiter = "\t"
    lineterminator = "\r\n"
    quoting = csv.QUOTE_NONE


csv.register_dialect("wordfast", WordfastDialect)


class WordfastTime:
    """Manages time stamps in the Wordfast format of YYYYMMDD~hhmmss."""

    def __init__(self, newtime=None):
        self._time = None
        if not newtime:
            self.time = None
        elif isinstance(newtime, str):
            self.timestring = newtime
        elif isinstance(newtime, time.struct_time):
            self.time = newtime

    def get_timestring(self):
        """Get the time in the Wordfast time format."""
        if not self._time:
            return None
        return time.strftime(WF_TIMEFORMAT, self._time)

    def set_timestring(self, timestring):
        """
        Set the time_sturct object using a Wordfast time formated string.

        :param timestring: A Wordfast time string (YYYMMDD~hhmmss)
        :type timestring: String
        """
        self._time = time.strptime(timestring, WF_TIMEFORMAT)

    timestring = property(get_timestring, set_timestring)

    def get_time(self):
        """Get the time_struct object."""
        return self._time

    def set_time(self, newtime):
        """
        Set the time_struct object.

        :param newtime: a new time object
        :type newtime: time.time_struct
        """
        if newtime and isinstance(newtime, time.struct_time):
            self._time = newtime
        else:
            self._time = None

    time = property(get_time, set_time)

    def __str__(self):
        if not self.timestring:
            return ""
        return self.timestring


class WordfastHeader:
    """A wordfast translation memory header."""

    def __init__(self, header=None):
        self._header_dict = []
        if not header:
            self.header = self._create_default_header()
        elif isinstance(header, dict):
            self.header = header

    @staticmethod
    def _create_default_header():
        """
        Create a default Wordfast header with the date set to the current
        time.
        """
        defaultheader = {}
        defaultheader.update(WF_FIELDNAMES_HEADER_DEFAULTS)
        defaultheader["date"] = f"%{WordfastTime(time.localtime()).timestring}"
        return defaultheader

    def getheader(self):
        """Get the header dictionary."""
        return self._header_dict

    def setheader(self, newheader):
        self._header_dict = newheader

    header = property(getheader, setheader)

    def settargetlang(self, newlang):
        self._header_dict["target-lang"] = f"%{newlang}"

    targetlang = property(None, settargetlang)

    def settucount(self, count):
        self._header_dict["tucount"] = "%%TU=%08d" % count

    tucount = property(None, settucount)


class WordfastUnit(base.TranslationUnit):
    """A Wordfast translation memory unit."""

    def __init__(self, source=None):
        self._dict = {}
        if source:
            self.source = source
        super().__init__(source)

    def _update_timestamp(self):
        """Refresh the timestamp for the unit."""
        self._dict["date"] = WordfastTime(time.localtime()).timestring

    def getdict(self):
        """Get the dictionary of values for a Wordfast line."""
        return self._dict

    def setdict(self, newdict):
        """
        Set the dictionary of values for a Wordfast line.

        :param newdict: a new dictionary with Wordfast line elements
        :type newdict: Dict
        """
        # TODO First check that the values are OK
        self._dict = newdict

    dict = property(getdict, setdict)

    def _get_source_or_target(self, key):
        if self._dict.get(key, None) is None:
            return None
        if self._dict[key]:
            return _wf_to_char(self._dict[key])
        return ""

    def _set_source_or_target(self, key, newvalue):
        if newvalue is None:
            self._dict[key] = None
        newvalue = _char_to_wf(newvalue)
        if key not in self._dict or newvalue != self._dict[key]:
            self._dict[key] = newvalue
            self._update_timestamp()

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

    def settargetlang(self, newlang):
        self._dict["target-lang"] = newlang

    targetlang = property(None, settargetlang)

    def __str__(self):
        return str(self._dict)

    def istranslated(self):
        if not self._dict.get("source", None):
            return False
        return bool(self._dict.get("target", None))


class WordfastTMFile(base.TranslationStore):
    """A Wordfast translation memory file."""

    Name = "Wordfast Translation Memory"
    Mimetypes = ["application/x-wordfast"]
    Extensions = ["txt"]
    UnitClass = WordfastUnit
    default_encoding = "iso-8859-1"

    def __init__(self, inputfile=None, **kwargs):
        """Construct a Wordfast TM, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = ""
        self.header = WordfastHeader()
        if inputfile is not None:
            self.parse(inputfile)

    def parse(self, input):
        """Parsese the given file or file source string."""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            tmsrc = input.read()
            input.close()
            input = tmsrc
        if TAB_UTF16 in input.split(b"\n")[0]:
            self.encoding = "utf-16"
        else:
            self.encoding = "iso-8859-1"
        try:
            input = input.decode(self.encoding)
        except Exception:
            raise ValueError(
                "Wordfast files are either UTF-16 (UCS2) or ISO-8859-1 encoded"
            )
        reader = csv.DictReader(
            input.split("\n"), fieldnames=WF_FIELDNAMES, dialect="wordfast"
        )
        for idx, line in enumerate(reader):
            if idx == 0:
                header = dict(
                    zip(WF_FIELDNAMES_HEADER, [line[key] for key in WF_FIELDNAMES])
                )
                self.header = WordfastHeader(header)
                continue
            newunit = WordfastUnit()
            newunit.dict = line
            self.addunit(newunit)

    def serialize(self, out):
        # Check first if there is at least one translated unit
        translated_units = [u for u in self.units if u.istranslated()]
        if not translated_units:
            return

        output = csv.StringIO()
        writer = csv.DictWriter(output, fieldnames=WF_FIELDNAMES, dialect="wordfast")
        # No real headers, the first line contains metadata
        self.header.tucount = len(translated_units)
        writer.writerow(
            dict(
                zip(
                    WF_FIELDNAMES,
                    [self.header.header[key] for key in WF_FIELDNAMES_HEADER],
                )
            )
        )

        for unit in translated_units:
            writer.writerow(unit.dict)
        out.write(output.getvalue().encode(self.encoding))
