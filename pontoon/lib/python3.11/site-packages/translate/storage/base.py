#
# Copyright 2006-2009 Zuza Software Foundation
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

"""Base classes for storage interfaces."""

from __future__ import annotations

import codecs
import logging
import pickle
from io import BytesIO
from itertools import starmap

from translate.misc.multistring import multistring
from translate.storage.placeables import StringElem
from translate.storage.placeables import parse as rich_parse
from translate.storage.workflow import StateEnum as states

# Simple BOM based encoding detection
ENCODING_BOMS = (
    (codecs.BOM_UTF8, "utf-8-sig"),
    (codecs.BOM_UTF16, "utf-16"),
    (codecs.BOM_UTF16_BE, "utf-16-be"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),
    (codecs.BOM_UTF32, "utf-32"),
    (codecs.BOM_UTF32_BE, "utf-32-be"),
    (codecs.BOM_UTF32_LE, "utf-32-le"),
)


class ParseError(Exception):
    def __init__(self, inner_exc):
        self.inner_exc = inner_exc

    def __str__(self):
        return repr(self.inner_exc)


class TranslationUnit:
    """
    Base class for translation units.

    Our concept of a *translation unit* is influenced heavily by `XLIFF
    <http://docs.oasis-open.org/xliff/xliff-core/xliff-core.html>`_.

    As such most of the method- and variable names borrows from XLIFF
    terminology.

    A translation unit consists of the following:

    - A *source* string. This is the original translatable text.
    - A *target* string. This is the translation of the *source*.
    - Zero or more *notes* on the unit. Notes would typically be some comments
      from a translator on the unit, or some comments originating from the
      source code.
    - Zero or more *locations*. Locations indicate where in the original source
      code this unit came from.
    - Zero or more *errors*. Some tools (eg.
      :mod:`~translate.filters.pofilter`) can run checks on translations and
      produce error messages.

    """

    rich_parsers = []
    """A list of functions to use for parsing a string into a rich string
    tree."""

    # State constants
    S_OBSOLETE = states.OBSOLETE
    S_EMPTY = states.EMPTY
    S_NEEDS_WORK = states.NEEDS_WORK
    S_REJECTED = states.REJECTED
    S_NEEDS_REVIEW = states.NEEDS_REVIEW
    S_UNREVIEWED = states.UNREVIEWED
    S_FINAL = states.FINAL

    # Elaborate state support could look something like this:
    # STATE = {
    #     S_OBSOLETE: (states.OBSOLETE, states.EMPTY),
    #     S_EMPTY: (states.EMPTY, states.NEEDS_WORK),
    #     S_NEEDS_WORK: (states.NEEDS_WORK, states.REJECTED),
    #     S_REJECTED: (states.REJECTED, states.NEEDS_REVIEW),
    #     S_NEEDS_REVIEW: (states.NEEDS_REVIEW, states.UNREVIEWED),
    #     S_UNREVIEWED: (states.UNREVIEWED, states.FINAL),
    #     S_FINAL: (states.FINAL, states.MAX),
    # }
    # """
    # Default supported states:
    #     * obsolete: The unit is not to be used.
    #     * empty: The unit has not been translated before.
    #     * needs work: Some translation has been done, but is not complete.
    #     * rejected: The unit has been reviewed, but was rejected.
    #     * needs review: The unit has been translated, but review was requested.
    #     * unreviewed: The unit has been translated, but not reviewed.
    #     * final: The unit is translated, reviewed and accepted.
    # """
    #
    # ... but by default a format will not support state:
    STATE = {}

    _store = None
    _source = None
    _target = None
    _rich_source = None
    _rich_target = None
    _state_n = 0
    notes = ""

    def __init__(self, source=None):
        """Constructs a TranslationUnit containing the given source string."""
        if source is not None:
            self.source = source

    def __eq__(self, other):
        """
        Compares two TranslationUnits.

        :type other: :class:`TranslationUnit`
        :param other: Another :class:`TranslationUnit`
        :rtype: Boolean
        :return: Returns *True* if the supplied :class:`TranslationUnit`
                 equals this unit.
        """
        return (
            self.source == other.source
            and self.target == other.target
            and self.getid() == other.getid()
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.source, self.target, self.getid()))

    def __str__(self):
        """Converts to a string representation. Most often overriden by subclasses."""
        # no point in showing store object.
        return ", ".join(
            f"{k}: {self.__dict__[k]}"
            for k in sorted(self.__dict__.keys())
            if k != "_store"
        )

    @classmethod
    def rich_to_multistring(cls, elem_list):
        """
        Convert a "rich" string tree to a ``multistring``.

        .. code-block:: pycon

            >>> from translate.storage.placeables.interfaces import X
            >>> rich = [StringElem(['foo', X(id='xxx', sub=[' ']), 'bar'])]
            >>> TranslationUnit.rich_to_multistring(rich)
            multistring('foo bar')
        """
        return multistring([str(elem) for elem in elem_list])

    def multistring_to_rich(self, mulstring):
        """
        Convert a multistring to a list of "rich" string trees.

        .. code-block:: pycon

            >>> target = multistring(['foo', 'bar', 'baz'])
            >>> TranslationUnit.multistring_to_rich(target)
            [<StringElem([<StringElem(['foo'])>])>,
             <StringElem([<StringElem(['bar'])>])>,
             <StringElem([<StringElem(['baz'])>])>]
        """
        if isinstance(mulstring, multistring):
            return [rich_parse(s, self.rich_parsers) for s in mulstring.strings]
        return [rich_parse(mulstring, self.rich_parsers)]

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        """Set the source string to the given value."""
        self._rich_source = None
        self._source = source

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        """Set the target string to the given value."""
        self._rich_target = None
        self._target = target

    @property
    def rich_source(self):
        """.. seealso:: :meth:`.rich_to_multistring`, :meth:`multistring_to_rich`."""
        if self._rich_source is None:
            self._rich_source = self.multistring_to_rich(self.source)
        return self._rich_source

    @rich_source.setter
    def rich_source(self, value):
        if not hasattr(value, "__iter__"):
            raise ValueError("value must be iterable")
        if len(value) < 1:
            raise ValueError("value must have at least one element.")
        if not isinstance(value[0], StringElem):
            raise TypeError("value[0] must be of type StringElem.")
        self._rich_source = list(value)
        multi = self.rich_to_multistring(value)
        if self.source != multi:
            self.source = multi

    @property
    def rich_target(self):
        """.. seealso:: :meth:`.rich_to_multistring`, :meth:`.multistring_to_rich`."""
        if self._rich_target is None:
            self._rich_target = self.multistring_to_rich(self.target)
        return self._rich_target

    @rich_target.setter
    def rich_target(self, value):
        if not hasattr(value, "__iter__"):
            raise ValueError("value must be iterable")
        if len(value) < 1:
            raise ValueError("value must have at least one element.")
        if not isinstance(value[0], StringElem):
            raise TypeError("value[0] must be of type StringElem.")
        self._rich_target = list(value)
        self.target = self.rich_to_multistring(value)

    def gettargetlen(self):
        """
        Returns the length of the target string.

        :rtype: Integer

        .. note::

           Plural forms might be combined.
        """
        length = len(self.target or "")
        strings = getattr(self.target, "strings", [])
        if strings:
            length += sum(len(pluralform) for pluralform in strings[1:])
        return length

    def getid(self):
        """
        A unique identifier for this unit.

        :rtype: string
        :return: an identifier for this unit that is unique in the store

        Derived classes should override this in a way that guarantees a unique
        identifier for each unit in the store.
        """
        return self.source

    def setid(self, value):
        """
        Sets the unique identified for this unit.

        only implemented if format allows ids independant from other unit
        properties like source or context
        """

    @staticmethod
    def getlocations():
        """
        A list of source code locations.

        :rtype: List

        .. note::

           Shouldn't be implemented if the format doesn't support it.
        """
        return []

    def addlocation(self, location):
        """
        Add one location to the list of locations.

        .. note::

           Shouldn't be implemented if the format doesn't support it.
        """

    def addlocations(self, location):
        """
        Add a location or a list of locations.

        .. note::

           Most classes shouldn't need to implement this, but should rather
           implement :meth:`TranslationUnit.addlocation`.

        .. warning::

           This method might be removed in future.
        """
        if isinstance(location, list):
            for item in location:
                self.addlocation(item)
        else:
            self.addlocation(location)

    @staticmethod
    def getcontext():
        """Get the message context."""
        return ""

    def setcontext(self, context):
        """Set the message context."""

    def getnotes(self, origin=None):
        """
        Returns all notes about this unit.

        It will probably be freeform text or something reasonable that can be
        synthesised by the format.
        It should not include location comments (see
        :meth:`~.TranslationUnit.getlocations`).
        """
        return getattr(self, "notes", "")

    def addnote(self, text, origin=None, position="append"):
        """
        Adds a note (comment).

        :type text: string
        :param text: Usually just a sentence or two.
        :type origin: string
        :param origin: Specifies who/where the comment comes from.
                       Origin can be one of the following text strings:
                       - 'translator'
                       - 'developer', 'programmer', 'source code' (synonyms)
        """
        if position == "append" and getattr(self, "notes", None):
            self.notes += "\n" + text
        else:
            self.notes = text

    def removenotes(self, origin=None):
        """Remove all the translator's notes."""
        self.notes = ""

    def adderror(self, errorname, errortext):
        """
        Adds an error message to this unit.

        :type errorname: string
        :param errorname: A single word to id the error.
        :type errortext: string
        :param errortext: The text describing the error.
        """

    @staticmethod
    def geterrors():
        """
        Get all error messages.

        :rtype: Dictionary
        """
        return {}

    def markreviewneeded(self, needsreview=True, explanation=None):
        """
        Marks the unit to indicate whether it needs review.

        :keyword needsreview: Defaults to True.
        :keyword explanation: Adds an optional explanation as a note.
        """

    def istranslated(self):
        """
        Indicates whether this unit is translated.

        This should be used rather than deducing it from .target,
        to ensure that other classes can implement more functionality
        (as XLIFF does).
        """
        return bool(self.target) and not self.isfuzzy()

    def istranslatable(self):
        """
        Indicates whether this unit can be translated.

        This should be used to distinguish real units for translation from
        header, obsolete, binary or other blank units.
        """
        return bool(self.source)

    def marktranslatable(self, value: bool) -> None:
        """Marks the unit as translateable or not."""

    @staticmethod
    def isfuzzy():
        """Indicates whether this unit is fuzzy."""
        return False

    def markfuzzy(self, value=True):
        """Marks the unit as fuzzy or not."""

    @staticmethod
    def isobsolete():
        """Indicate whether a unit is obsolete."""
        return False

    def makeobsolete(self):
        """Make a unit obsolete."""

    @staticmethod
    def isheader():
        """Indicates whether this unit is a header."""
        return False

    @staticmethod
    def isreview():
        """Indicates whether this unit needs review."""
        return False

    def isblank(self):
        """
        Used to see if this unit has no source or target string.

        .. note::

           This is probably used more to find translatable units,
           and we might want to move in that direction rather and
           get rid of this.
        """
        return not (self.source or self.target)

    @staticmethod
    def hasplural():
        """Tells whether or not this specific unit has plural strings."""
        # TODO: Reconsider
        return False

    def getsourcelanguage(self):
        return self._store.getsourcelanguage()

    def gettargetlanguage(self):
        return self._store.gettargetlanguage()

    def merge(self, otherunit, overwrite=False, comments=True, authoritative=False):
        """Do basic format agnostic merging."""
        if not self.target or overwrite:
            self.rich_target = otherunit.rich_target

    def unit_iter(self):
        """Iterator that only returns this unit."""
        yield self

    def getunits(self):
        """This unit in a list."""
        return [self]

    @classmethod
    def buildfromunit(cls, unit):
        """
        Build a native unit from a foreign unit.

        Preserving as much information as possible.
        """
        if type(unit) is cls and hasattr(unit, "copy") and callable(unit.copy):
            return unit.copy()
        newunit = cls(unit.source)
        newunit.target = unit.target
        newunit.markfuzzy(unit.isfuzzy())
        newunit.setid(unit.getid())
        locations = unit.getlocations()
        if locations:
            newunit.addlocations(locations)
        notes = unit.getnotes()
        if notes:
            newunit.addnote(notes)
        return newunit

    xid = property(lambda self: None, lambda self, value: None)
    rid = property(lambda self: None, lambda self, value: None)

    def get_state_id(self, n=None):
        if n is None:
            n = self.get_state_n()
        for state_id, state_range in self.STATE.items():
            if state_range[0] <= n < state_range[1]:
                return state_id
        if self.STATE:
            raise ValueError(f"No state containing value {n}")
        return n

    def get_state_n(self):
        if self.STATE:
            return self._state_n
        return self.S_UNREVIEWED if self.istranslated() else self.S_EMPTY

    def set_state_n(self, value):
        self._state_n = value

    def infer_state(self):
        """
        Empty method that should be overridden in sub-classes to infer the
        current state(_n) of the unit from its current state.
        """

    @staticmethod
    def sync_plural_count(
        target: list[str] | str | multistring, plural_tags: list[str]
    ) -> list[str]:
        """Ensure that plural count in string matches tags definition."""
        # Get string list to handle, wrapping non multistring/list targets into a list.
        if isinstance(target, multistring):
            # Coerce all items to string, they might be multistrings
            plural_strings = [str(string) for string in target.strings]
        elif isinstance(target, list):
            plural_strings = target
        else:
            plural_strings = [target]

        # Add missing strings
        missing = len(plural_tags) - len(plural_strings)
        if missing:
            plural_strings += [""] * missing

        # Remove extra ones
        return plural_strings[: len(plural_tags)]


class TranslationStore:
    """Base class for stores for multiple translation units of type UnitClass."""

    UnitClass = TranslationUnit
    """The class of units that will be instantiated and used by this class"""
    Name = "Base translation store"
    """The human usable name of this store type"""
    Mimetypes = None
    """A list of MIME types associated with this store type"""
    Extensions = None
    """A list of file extentions associated with this store type"""
    _binary = False
    """Indicates whether a file should be accessed as a binary file."""
    suggestions_in_format = False
    """Indicates if format can store suggestions and alternative translation
    for a unit"""

    default_encoding = "utf-8"
    sourcelanguage = None
    targetlanguage = None

    def __init__(self, unitclass=None, encoding=None):
        """Construct a blank TranslationStore."""
        self.units = []
        if unitclass:
            self.UnitClass = unitclass
        self._encoding = encoding
        self.locationindex = {}
        self.sourceindex = {}
        self.id_index = {}

    @property
    def encoding(self):
        # self._encoding is either defined by __init__ or auto-detected from parsed file
        if self._encoding == "auto":
            return "utf-8"
        return self._encoding or self.default_encoding

    @encoding.setter
    def encoding(self, value):
        if value == "CHARSET" or value is None:
            return
        if value == "ascii":
            value = "utf-8"
        self._encoding = value

    def getsourcelanguage(self):
        """Get the source language for this store."""
        return self.sourcelanguage

    def setsourcelanguage(self, sourcelanguage):
        """Set the source language for this store."""
        self.sourcelanguage = sourcelanguage

    def gettargetlanguage(self):
        """Get the target language for this store."""
        return self.targetlanguage

    def settargetlanguage(self, targetlanguage):
        """Set the target language for this store."""
        self.targetlanguage = targetlanguage

    def getprojectstyle(self):
        """Get the project type for this store."""
        return getattr(self, "_project_style", None)

    def setprojectstyle(self, project_style):
        """Set the project type for this store."""
        self._project_style = project_style

    def unit_iter(self):
        """Iterator over all the units in this store."""
        yield from self.units

    def getunits(self):
        """Return a list of all units in this store."""
        return list(self.unit_iter())

    def addunit(self, unit):
        """
        Append the given unit to the object's list of units.

        This method should always be used rather than trying to modify the
        list manually.

        :type unit: :class:`TranslationUnit`
        :param unit: The unit that will be added.
        """
        unit._store = self
        self.units.append(unit)

    def removeunit(self, unit):
        """
        Remove the given unit to the object's list of units.

        This method should always be used rather than trying to modify the
        list manually.

        :type unit: :class:`TranslationUnit`
        :param unit: The unit that will be added.
        """
        self.units.remove(unit)
        self.remove_unit_from_index(unit)

    def addsourceunit(self, source):
        """
        Add and returns a new unit with the given source string.

        :rtype: :class:`TranslationUnit`
        """
        unit = self.UnitClass(source)
        self.addunit(unit)
        return unit

    def findid(self, id):
        """Find unit with matching id by checking id_index."""
        self.require_index()
        return self.id_index.get(id)

    def findunit(self, source):
        """
        Find the unit with the given source string.

        :rtype: :class:`TranslationUnit` or None
        """
        self.require_index()
        if source in self.sourceindex:
            return self.sourceindex[source][0]
        return None

    def findunits(self, source):
        """
        Find the units with the given source string.

        :rtype: :class:`TranslationUnit` or None
        """
        self.require_index()
        if source in self.sourceindex:
            return self.sourceindex[source]
        return None

    def translate(self, source):
        """
        Return the translated string for a given source string.

        :rtype: String or None
        """
        unit = self.findunit(source)
        if unit and unit.target:
            return unit.target
        return None

    def remove_unit_from_index(self, unit):
        """Remove a unit from source and locaton indexes."""

        def remove_source(source):
            if source in self.sourceindex:
                self.sourceindex[source].remove(unit)
                if len(self.sourceindex[source]) == 0:
                    del self.sourceindex[source]

        if unit.hasplural():
            for source in unit.source.strings:
                remove_source(source)
        else:
            remove_source(unit.source)

        for location in unit.getlocations():
            if (
                location in self.locationindex
                and self.locationindex[location] is not None
                and self.locationindex[location] == unit
            ):
                del self.locationindex[location]

    def add_unit_to_index(self, unit):
        """Add a unit to source and location idexes."""
        self.id_index[unit.getid()] = unit

        def insert_unit(source):
            if source not in self.sourceindex:
                self.sourceindex[source] = [unit]
            else:
                self.sourceindex[source].append(unit)

        if unit.hasplural():
            for source in unit.source.strings:
                insert_unit(source)
        else:
            insert_unit(unit.source)

        for location in unit.getlocations():
            # If locations aren't unique, keep the first unit.
            if location not in self.locationindex:
                # FIXME: maybe better store a list of units like sourceindex in
                # case there are several units with the same location.
                self.locationindex[location] = unit

    def makeindex(self):
        """
        Indexes the items in this store. At least .sourceindex should be
        useful.
        """
        self.locationindex = {}
        self.sourceindex = {}
        self.id_index = {}
        for index, unit in enumerate(self.units):
            unit.index = index
            if not (unit.isheader() or unit.isblank()):
                self.add_unit_to_index(unit)

    def require_index(self):
        """Make sure source index exists."""
        if not self.id_index:
            self.makeindex()

    def getids(self):
        """Return a list of unit ids."""
        self.require_index()
        return self.id_index.keys()

    def __getstate__(self):
        odict = self.__dict__.copy()
        # fileobj is generally not picklable
        odict["fileobj"] = None
        return odict

    def __bytes__(self):
        out = BytesIO()
        self.serialize(out)
        return out.getvalue()

    def serialize(self, out):
        """
        Converts to a bytes representation that can be parsed back using
        :meth:`~.TranslationStore.parsestring`.
        `out` should be an open file-like objects to write to.
        """
        out.write(pickle.dumps(self))

    def isempty(self):
        """Return True if the object doesn't contain any translation units."""
        if len(self.units) == 0:
            return True
        return all(not unit.istranslatable() for unit in self.units)

    def _assignname(self):
        """
        Tries to work out what the name of the filesystem file is and
        assigns it to .filename.
        """
        fileobj = getattr(self, "fileobj", None)
        if fileobj:
            filename = getattr(fileobj, "name", None)
            if not filename:
                filename = getattr(fileobj, "filename", None)
            if filename:
                self.filename = filename

    @classmethod
    def parsestring(cls, storestring):
        """Convert the string representation back to an object."""
        newstore = cls()
        if isinstance(storestring, str):
            # parse() is expecting bytes
            storestring = storestring.encode(cls.default_encoding)
        newstore.parse(storestring)
        return newstore

    @staticmethod
    def fallback_detection(text):
        """Simple detection based on BOM in case chardet is not available."""
        for bom, encoding in ENCODING_BOMS:
            if text.startswith(bom):
                return {"encoding": encoding, "confidence": 1.0}
        return None

    def detect_encoding(
        self, text: bytes, default_encodings: list[str] | None = None
    ) -> tuple[str, str]:
        """
        Try to detect a file encoding from `text`, using either the chardet lib
        or by trying to decode the file.
        """
        if not default_encodings:
            default_encodings = ["utf-8"]
        try:
            from charset_normalizer import detect
        except ImportError:
            detected_encoding = self.fallback_detection(text)
        else:
            detected_encoding = detect(text)
            if (
                detected_encoding["confidence"] is None
                or detected_encoding["confidence"] < 0.48
            ):
                detected_encoding = None
            elif detected_encoding["encoding"] == "ascii":
                detected_encoding["encoding"] = self.encoding
            else:
                detected_encoding["encoding"] = detected_encoding["encoding"].lower()

        encodings = []
        # Purposefully accessed the internal _encoding, as encoding is never 'auto'
        if self._encoding == "auto":
            if detected_encoding and detected_encoding["encoding"] not in encodings:
                encodings.append(detected_encoding["encoding"])
            for encoding in default_encodings:
                if encoding not in encodings:
                    encodings.append(encoding)
        elif detected_encoding:
            if "-" in detected_encoding["encoding"]:
                encoding, suffix = detected_encoding["encoding"].rsplit("-", 1)
            else:
                encoding = detected_encoding["encoding"]
                suffix = None

            # Different charset, just with BOM
            if encoding == self.encoding and suffix == "sig":
                encodings.append(detected_encoding["encoding"])
            elif detected_encoding["encoding"] != self.encoding:
                logging.warning(
                    "trying to parse %s with encoding: %s but "
                    "detected encoding is %s (confidence: %s)",
                    self.filename,
                    self.encoding,
                    detected_encoding["encoding"],
                    detected_encoding["confidence"],
                )
            encodings.append(self.encoding)
        else:
            encodings.append(self.encoding)

        for encoding in encodings:
            try:
                r_text = str(text, encoding)
                r_encoding = encoding
                break
            except UnicodeDecodeError:
                r_text = None
                r_encoding = None
        if r_encoding == "ascii":
            r_encoding = "utf-8"
        return r_text, r_encoding

    def parse(self, data):
        """Parser to process the given source string."""
        self.units = pickle.loads(data).units

    def savefile(self, storefile):
        """Write the string representation to the given file (or filename)."""
        if isinstance(storefile, str):
            storefile = open(storefile, "wb")
        self.fileobj = storefile
        self._assignname()
        self.serialize(storefile)
        storefile.close()

    def save(self):
        """Save to the file that data was originally read from, if available."""
        fileobj = getattr(self, "fileobj", None)
        if not fileobj:
            if hasattr(self, "filename"):
                fileobj = open(self.filename, "wb")
        else:
            fileobj.close()
            filename = getattr(fileobj, "name", getattr(fileobj, "filename", None))
            if not filename:
                raise ValueError("No file or filename to save to")
            fileobj = open(filename, "wb")
        self.savefile(fileobj)

    @classmethod
    def _from_handle(cls, storehandle):
        storestring = storehandle.read()
        newstore = cls.parsestring(storestring)
        newstore.fileobj = storehandle
        newstore._assignname()
        return newstore

    @classmethod
    def parsefile(cls, storefile):
        """
        Reads the given file (or opens the given filename) and parses back
        to an object.
        """
        if isinstance(storefile, str):
            with open(storefile, "rb") as storehandle:
                return cls._from_handle(storehandle)
        mode = getattr(storefile, "mode", "rb")
        # For some reason GzipFile returns 1, so we have to test for that here
        if mode == 1 or "r" in mode:
            newstore = cls._from_handle(storefile)
            storefile.close()
            return newstore

        newstore = cls()
        newstore.fileobj = storefile
        newstore._assignname()
        return newstore

    @property
    def merge_on(self):
        """
        The matching criterion to use when merging on.

        :return: The default matching criterion for all the subclasses.
        :rtype: string
        """
        return "id"


class UnitId:
    KEY_SEPARATOR = "."
    INDEX_SEPARATOR = ""

    def __init__(self, parts):
        self.parts = parts

    def __str__(self):
        def fmt(element, key):
            if element == "key":
                return f"{self.KEY_SEPARATOR}{key}"
            if element == "index":
                return f"{self.INDEX_SEPARATOR}[{key}]"
            raise ValueError(f"Unsupported element: {element}")

        return "".join(starmap(fmt, self.parts))

    def extend(self, key, value):
        return self.__class__([*self.parts, (key, value)])

    @classmethod
    def from_string(cls, text):
        result = []
        # Strip possible leading separator
        text = text.removeprefix(cls.KEY_SEPARATOR)
        for item in text.split(cls.KEY_SEPARATOR):
            bracepos = item.find("[")
            endbracepos = item.find("]")
            while (
                (bracepos := item.find("[")) != -1
                and (endbracepos := item.find("]")) != -1
                and item[bracepos + 1 : endbracepos].isdigit()
            ):
                if bracepos > 0:
                    result.append(("key", item[:bracepos]))
                    item = item[bracepos:]
                    endbracepos -= bracepos
                    bracepos = 0
                result.append(("index", int(item[bracepos + 1 : endbracepos])))
                item = item[endbracepos + 1 :]
            if item:
                result.append(("key", item))
        if not result:
            result.append(("key", ""))
        return cls(result)

    def __eq__(self, other):
        return self.parts == other.parts

    def __repr__(self):
        return f"<UnitId:{self.parts}>"


class DictUnit(TranslationUnit):
    IdClass = UnitId

    def __init__(self, source=None):
        super().__init__(source)
        self._unitid = None

    def get_unitid(self):
        if self._unitid is None:
            self._unitid = self.IdClass.from_string(self._id)
        return self._unitid

    def storevalue(self, output, value, override_key=None, unset=False):
        parent = target = output
        parts = self.get_unitid().parts
        key = None
        for pos, part in enumerate(parts[:-1]):
            element, key = part
            use_list = parts[pos + 1][0] == "index"
            default = [] if use_list else {}
            if element == "index":
                while len(target) <= key and not unset:
                    target.append(default.copy())
            elif element == "key":
                if key not in target or isinstance(target[key], str):
                    target[key] = default
            else:
                raise ValueError(f"Unsupported element: {element}")
            if not use_list and isinstance(target[key], list):
                # Convert list to dict if needed
                target[key] = dict(enumerate(target[key]))
            # Handle placeholders
            if target[key] is None:
                target[key] = default.copy()
            parent = target
            target = target[key]
        if override_key:
            child_element, child_key = "key", override_key
        else:
            child_element, child_key = parts[-1]
        if child_element == "key":
            if unset:
                del target[child_key]
                # Remove empty dict from parent
                if not target and key:
                    del parent[key]
            else:
                target[child_key] = value
        elif child_element == "index":
            if len(target) <= child_key:
                if not unset:
                    # Add placeholders to the list
                    while len(target) < child_key:
                        target.append(None)
                    target.append(value)
            elif unset:
                del target[child_key]
            else:
                target[child_key] = value
        else:
            raise ValueError(f"Unsupported element: {child_element}")

    def storevalues(self, output):
        self.storevalue(output, self.value)

    def getvalue(self):
        """Returns dictionary for serialization."""
        result = {}
        self.storevalues(result)
        return result

    def setid(self, value, unitid=None):
        self._id = value
        self._unitid = unitid

    def set_unitid(self, unitid):
        # Set _unitid first to avoid need to re-construct it from id
        self.setid(str(unitid), unitid)


class DictStore(TranslationStore):
    def get_root_node(self):
        if self.units and all(
            unit.get_unitid().parts[0][0] == "index" for unit in self.units
        ):
            return []
        return {}

    def serialize_units(self, output):
        for unit in self.unit_iter():
            unit.storevalues(output)
