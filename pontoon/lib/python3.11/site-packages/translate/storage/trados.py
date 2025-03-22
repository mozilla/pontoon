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

r"""
Manage the Trados .txt Translation Memory format.

A Trados file looks like this:

.. code-block:: xml

    <TrU>
    <CrD>18012000, 13:18:35
    <CrU>CAROL-ANN
    <UsC>0
    <Seg L=EN_GB>Association for Road Safety \endash  Conference
    <Seg L=DE_DE>Tagung der Gesellschaft für Verkehrssicherheit
    </TrU>
    <TrU>
    <CrD>18012000, 13:19:14
    <CrU>CAROL-ANN
    <UsC>0
    <Seg L=EN_GB>Road Safety Education in our Schools
    <Seg L=DE_DE>Verkehrserziehung an Schulen
    </TrU>

"""

import re
import time

from translate.storage import base

try:
    # FIXME see if we can't use lxml
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError(
        "BeautifulSoup 4 is not installed. Support for Trados txt is disabled."
    )


__all__ = (
    "RTF_ESCAPES",
    "TRADOS_TIMEFORMAT",
    "TradosTxtDate",
    "TradosTxtTmFile",
    "TradosUnit",
    "escape",
    "unescape",
)


TRADOS_TIMEFORMAT = "%d%m%Y, %H:%M:%S"
"""Time format used by Trados .txt"""

RTF_ESCAPES = {
    "\\emdash": "—",
    "\\endash": "–",
    # Nonbreaking space equal to width of character "m" in current font.
    "\\emspace": "\u2003",
    # Nonbreaking space equal to width of character "n" in current font.
    "\\enspace": "\u2002",
    # "\\qmspace": "",    # One-quarter em space.
    "\\bullet": "•",  # Bullet character.
    "\\lquote": "‘",  # Left single quotation mark. \u2018
    "\\rquote": "’",  # Right single quotation mark. \u2019
    "\\ldblquote": "“",  # Left double quotation mark. \u201C
    "\\rdblquote": "”",  # Right double quotation mark. \u201D
    "\\~": "\u00a0",  # Nonbreaking space
    "\\-": "\u00ad",  # Optional hyphen.
    "\\_": "‑",  # Nonbreaking hyphen \U2011
    # A hexadecimal value, based on the specified character set (may be used to
    # identify 8-bit values).
    # "\\'hh": "",
}
"""RTF control to Unicode map. See
http://msdn.microsoft.com/en-us/library/aa140283(v=office.10).aspx
"""


def unescape(text):
    """Convert Trados text to normal Unicode string."""
    for trados_escape, char in RTF_ESCAPES.items():
        text = text.replace(trados_escape, char)
    return text


def escape(text):
    """Convert Unicode string to Trodas escapes."""
    for trados_escape, char in RTF_ESCAPES.items():
        text = text.replace(char, trados_escape)
    return text


class TradosTxtDate:
    """Manages the timestamps in the Trados .txt format of DDMMYYY, hh:mm:ss."""

    def __init__(self, newtime=None):
        self._time = None
        if newtime:
            if isinstance(newtime, str):
                self.timestring = newtime
            elif isinstance(newtime, time.struct_time):
                self.time = newtime

    def get_timestring(self):
        """Get the time in the Trados time format."""
        if not self._time:
            return None
        return time.strftime(TRADOS_TIMEFORMAT, self._time)

    def set_timestring(self, timestring):
        """
        Set the time_struct object using a Trados time formated string.

        :param timestring: A Trados time string (DDMMYYYY, hh:mm:ss)
        :type timestring: String
        """
        self._time = time.strptime(timestring, TRADOS_TIMEFORMAT)

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


class TradosUnit(base.TranslationUnit):
    def __init__(self, source=None):
        self._soup = None
        super().__init__(source)

    @property
    def source(self):
        return unescape(self._soup.findAll("seg")[0].contents[0])

    @source.setter
    def source(self, source):
        pass

    def gettarget(self):
        return unescape(self._soup.findAll("seg")[1].contents[0])

    target = property(gettarget, None)


class TradosSoup(BeautifulSoup):
    MARKUP_MASSAGE = [
        (
            re.compile("<(?P<fulltag>(?P<tag>[^\\s\\/]+).*?)>(?P<content>.+)\r"),
            lambda x: "<{fulltag}>{content}</{tag}>".format(**x.groupdict()),
        ),
    ]


class TradosTxtTmFile(base.TranslationStore):
    """A Trados translation memory file."""

    Name = "Trados Translation Memory"
    Mimetypes = ["application/x-trados-tm"]
    Extensions = ["txt"]
    UnitClass = TradosUnit
    default_encoding = "iso-8859-1"

    def __init__(self, inputfile=None, **kwargs):
        """Construct a Wordfast TM, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = ""
        if inputfile is not None:
            self.parse(inputfile)

    def parse(self, input):
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            tmsrc = input.read()
            input.close()
            input = tmsrc
        self._soup = TradosSoup(input)
        for tu in self._soup.findAll("tru"):
            unit = TradosUnit()
            unit._soup = TradosSoup(str(tu))
            self.addunit(unit)

    def serialize(self, out):
        # FIXME turn the lowercased tags back into mixed case
        out.write(self._soup.prettify())
