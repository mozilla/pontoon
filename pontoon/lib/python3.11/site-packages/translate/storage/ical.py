#
# Copyright 2007-2008 Zuza Software Foundation
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
Class that manages iCalender files for translation.

iCalendar files follow the `RFC2445 <https://tools.ietf.org/html/rfc2445>`_
specification.

The iCalendar specification uses the following naming conventions:

- Component: an event, journal entry, timezone, etc
- Property: a property of a component: summary, description, start time, etc
- Attribute: an attribute of a property, e.g. language

The following are localisable in this implementation:

- VEVENT component: SUMMARY, DESCRIPTION, COMMENT and LOCATION properties

While other items could be localised this is not seen as important until use
cases arise.  In such a case simply adjusting the component.name and
property.name lists to include these will allow expanded localisation.

LANGUAGE Attribute
    While the iCalendar format allows items to have a language attribute this is
    not used. The reason being that for most of the items that we localise they
    are only allowed to occur zero or once.  Thus 'summary' would ideally
    be present in multiple languages in one file, the format does not allow
    such multiple entries.  This is unfortunate as it prevents the creation
    of a single multilingual iCalendar file.

Future Format Support
    As this format used `vobject <http://eventable.github.io/vobject/>`_
    which supports various formats including
    :wp:`vCard` it is possible to expand
    this format to understand those if needed.
"""

import re
from io import BytesIO

import vobject

from translate.storage import base

ICAL_UNIT_LOCATION_RE = re.compile("\\[(?P<uid>.+)\\](?P<property>.+)")


class icalunit(base.TranslationUnit):
    """An ical entry that is translatable."""

    def __init__(self, source=None, **kwargs):
        self.location = ""
        if source:
            self.source = source
        super().__init__(source)

    def addlocation(self, location):
        self.location = location

    def getlocations(self):
        return [self.location]


class icalfile(base.TranslationStore):
    """An ical file."""

    UnitClass = icalunit

    def __init__(self, inputfile=None, **kwargs):
        """Construct an ical file, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = ""
        self._icalfile = None
        if inputfile is not None:
            self.parse(inputfile)

    def serialize(self, out):
        _outicalfile = self._icalfile
        for unit in self.units:
            for location in unit.getlocations():
                match = ICAL_UNIT_LOCATION_RE.match(location)
                for component in self._icalfile.components():
                    if component.name != "VEVENT":
                        continue
                    if component.uid.value != match.groupdict()["uid"]:
                        continue
                    for property in component.getChildren():
                        if property.name == match.groupdict()["property"]:
                            property.value = unit.target

        if _outicalfile:
            _outicalfile.serialize(out)

    def parse(self, input):
        """Parse the given file or file source string."""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if isinstance(input, BytesIO):
            input = input.getvalue()
        elif hasattr(input, "read"):
            inisrc = input.read()
            input.close()
            input = inisrc
        if isinstance(input, bytes):
            input = input.decode(self.encoding)
        self._icalfile = next(vobject.readComponents(input))

        for component in self._icalfile.components():
            if component.name == "VEVENT":
                for property in component.getChildren():
                    if property.name in {
                        "SUMMARY",
                        "DESCRIPTION",
                        "COMMENT",
                        "LOCATION",
                    }:
                        newunit = self.addsourceunit(property.value)
                        newunit.addnote(f"Start date: {component.dtstart.value}")
                        newunit.addlocation(f"[{component.uid.value}]{property.name}")
