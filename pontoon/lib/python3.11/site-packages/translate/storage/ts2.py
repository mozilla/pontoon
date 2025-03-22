#
# Copyright 2008-2011 Zuza Software Foundation
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
Module for handling Qt linguist (.ts) files.

This will eventually replace the older ts.py which only supports the older
format. While converters haven't been updated to use this module, we retain
both.

`TS file format 4.3 <http://doc.qt.io/archives/4.3/linguist-ts-file-format.html>`_,
`4.8 <http://doc.qt.io/qt-4.8/linguist-ts-file-format.html>`_,
`5 <http://doc.qt.io/qt-5/linguist-ts-file-format.html>`_.
`Example <http://svn.ez.no/svn/ezcomponents/trunk/Translation/docs/linguist-format.txt>`_.

`Specification of the valid variable entries <http://doc.qt.io/qt-5/qstring.html#arg>`_,
`2 <http://doc.qt.io/qt-5/qstring.html#arg-2>`_
"""

from lxml import etree

from translate.lang import data
from translate.misc.multistring import multistring
from translate.misc.xml_helpers import safely_set_text
from translate.storage import lisa
from translate.storage.placeables import general
from translate.storage.workflow import StateEnum as state

# TODO: handle translation types


# Encode some characters same as lupdate, this matches tsProtect implementation:
#
# - quote and apostrophe
# - any whitespace character above 0x7f
#
# The latter can be generated using:
# >>> for i in  range(sys.maxunicode):
# ...     if i > 0x7f and chr(i).isspace():
# ...         print(f'   {chr(i)!r}: "&#x{i:x};",')

OUTPUT_TRANS = str.maketrans(
    {
        "'": "&apos;",
        '"': "&quot;",
        "\xa0": "&#xa0;",
        "\u1680": "&#x1680;",
        "\u2000": "&#x2000;",
        "\u2001": "&#x2001;",
        "\u2002": "&#x2002;",
        "\u2003": "&#x2003;",
        "\u2004": "&#x2004;",
        "\u2005": "&#x2005;",
        "\u2006": "&#x2006;",
        "\u2007": "&#x2007;",
        "\u2008": "&#x2008;",
        "\u2009": "&#x2009;",
        "\u200a": "&#x200a;",
        "\u2028": "&#x2028;",
        "\u2029": "&#x2029;",
        "\u202f": "&#x202f;",
        "\u205f": "&#x205f;",
        "\u3000": "&#x3000;",
    }
)


class tsunit(lisa.LISAunit):
    """A single term in the TS file."""

    rootNode = "message"
    languageNode = "source"
    textNode = ""
    namespace = ""
    rich_parsers = general.parsers

    S_OBSOLETE = state.OBSOLETE
    S_UNTRANSLATED = state.EMPTY
    S_FUZZY = state.NEEDS_WORK
    S_TRANSLATED = state.UNREVIEWED

    statemap = {
        "obsolete": S_OBSOLETE,
        "unfinished": S_FUZZY,
        "": S_TRANSLATED,
        None: S_TRANSLATED,
    }
    """This maps the unit "type" attribute to state."""

    STATE = {
        S_OBSOLETE: (state.OBSOLETE, state.EMPTY),
        S_UNTRANSLATED: (state.EMPTY, state.NEEDS_WORK),
        S_FUZZY: (state.NEEDS_WORK, state.UNREVIEWED),
        S_TRANSLATED: (state.UNREVIEWED, state.MAX),
    }

    statemap_r = {i[1]: i[0] for i in statemap.items()}
    _context = None
    _locations = None

    def createlanguageNode(self, lang, text, purpose):
        """Returns an xml Element setup with given parameters."""
        assert purpose
        if purpose == "target":
            purpose = "translation"
        langset = etree.Element(self.namespaced(purpose))
        # TODO: check language
        # lisa.setXMLlang(langset, lang)

        safely_set_text(langset, text)
        return langset

    def _getsourcenode(self):
        return self.xmlelement.find(self.namespaced(self.languageNode))

    def _gettargetnode(self):
        result = self.xmlelement.find(self.namespaced("translation"))
        if result is not None:
            return result
        return etree.SubElement(self.xmlelement, self.namespaced("translation"))

    def getlanguageNodes(self):
        """We override this to get source and target nodes."""
        return [
            n for n in [self._getsourcenode(), self._gettargetnode()] if n is not None
        ]

    @lisa.LISAunit.source.getter
    def source(self):
        sourcenode = self._getsourcenode()
        if sourcenode is None:
            return None
        # TODO: support <byte>. See bug 528.
        text = sourcenode.text
        if self.hasplural():
            return multistring([text])
        return text

    @property
    def target(self):
        targetnode = self._gettargetnode()
        if self.hasplural():
            numerus_nodes = targetnode.findall(self.namespaced("numerusform"))
            return multistring([node.text or "" for node in numerus_nodes])
        return targetnode.text or ""

    @target.setter
    def target(self, target):
        # This is a fairly destructive implementation. Don't assume that this
        # is necessarily correct in all regards, but it does deal with a lot of
        # cases. It is hard to deal with plurals.
        #
        # Firstly deal with reinitialising to None or setting to identical
        # string.
        self._rich_target = None
        if self.target == target:
            return
        strings = []
        if isinstance(target, multistring):
            strings = target.strings
        elif isinstance(target, list):
            strings = target
        else:
            strings = [target]
        targetnode = self._gettargetnode()
        type = targetnode.get("type")
        targetnode.clear()
        if type:
            targetnode.set("type", type)
        if self.hasplural() or len(strings) > 1:
            self.xmlelement.set("numerus", "yes")
            for string in strings:
                numerus = etree.SubElement(targetnode, self.namespaced("numerusform"))
                safely_set_text(numerus, string or "")
        else:
            safely_set_text(targetnode, target or "")

    def hasplural(self):
        return self.xmlelement.get("numerus") == "yes"

    def addnote(self, text, origin=None, position="append"):
        """Add a note specifically in the appropriate *comment* tag."""
        current_notes = self.getnotes(origin)
        self.removenotes(origin)
        if origin in {"programmer", "developer", "source code"}:
            note = etree.SubElement(self.xmlelement, self.namespaced("extracomment"))
        else:
            note = etree.SubElement(
                self.xmlelement, self.namespaced("translatorcomment")
            )
        if position == "append":
            safely_set_text(
                note, "\n".join(item for item in [current_notes, text.strip()] if item)
            )
        else:
            safely_set_text(note, text.strip())

    def getnotes(self, origin=None):
        # TODO: consider only responding when origin has certain values
        comments = []
        if origin in {"programmer", "developer", "source code", None}:
            notenode = self.xmlelement.find(self.namespaced("extracomment"))
            if notenode is not None and notenode.text is not None:
                comments.append(notenode.text)
        if origin in {"translator", None}:
            notenode = self.xmlelement.find(self.namespaced("translatorcomment"))
            if notenode is not None and notenode.text is not None:
                comments.append(notenode.text)
        return "\n".join(comments)

    def removenotes(self, origin=None):
        """Remove all the translator notes."""
        if origin in {"programmer", "developer", "source code", None}:
            note = self.xmlelement.find(self.namespaced("extracomment"))
            if note is not None:
                self.xmlelement.remove(note)
        if origin in {"translator", None}:
            note = self.xmlelement.find(self.namespaced("translatorcomment"))
            if note is not None:
                self.xmlelement.remove(note)

    def _gettype(self):
        """Returns the type of this translation."""
        return self._gettargetnode().get("type")

    def _settype(self, value=None):
        """Set the type of this translation."""
        if value:
            self._gettargetnode().set("type", value)
        elif self._gettype():
            # lxml recommends against using .attrib, but there seems to be no
            # other way
            self._gettargetnode().attrib.pop("type")

    def isreview(self):
        """States whether this unit needs to be reviewed."""
        return self._gettype() == "unfinished"

    def isfuzzy(self):
        return self._gettype() == "unfinished" and bool(self.target)

    def markfuzzy(self, value=True):
        if value:
            self._settype("unfinished")
        else:
            self._settype(None)

    def getid(self):
        context_name = self.getcontext()
        if self.source is None and context_name is None:
            return None

        # XXX: context_name is not supposed to be able to be None (the <name>
        # tag is compulsary in the <context> tag)
        if context_name is not None:
            if self.source:
                return context_name + self.source
            return context_name
        return self.source

    def istranslatable(self):
        # Found a file in the wild with no context and an empty source. This
        # served as a header, so let's classify this as not translatable.
        # http://bibletime.svn.sourceforge.net/viewvc/bibletime/trunk/bibletime/i18n/messages/bibletime_ui.ts
        # Furthermore, let's decide to handle obsolete units as untranslatable
        # like we do with PO.
        return bool(self.getid()) and not self.isobsolete()

    def getcontextname(self):
        parent = self.xmlelement.getparent()
        if parent is None:
            if self._context:
                return self._context
            return None
        context = parent.find("name")
        if context is None:
            return None
        return context.text

    def setcontext(self, value):
        if value == self.getcontextname():
            return
        parent = self.xmlelement.getparent()
        if parent is None:
            self._context = value
        # TODO: if unit is inserted to ts store
        # it should put unit in correct context
        # if unit is already in store it should move
        # and adjust store as necessary

    def getcontext(self):
        contexts = [self.getcontextname()]
        commentnode = self.xmlelement.find(self.namespaced("comment"))
        if commentnode is not None and commentnode.text is not None:
            contexts.append(commentnode.text)
        message_id = self.xmlelement.get("id")
        if message_id is not None:
            contexts.append(message_id)
        contexts = filter(None, contexts)
        return "\n".join(contexts)

    def addlocation(self, location):
        self._locations = None
        newlocation = etree.SubElement(self.xmlelement, self.namespaced("location"))
        try:
            filename, line = location.split(":", 1)
        except ValueError:
            filename = location
            line = None
        newlocation.set("filename", filename)
        if line is not None:
            newlocation.set("line", line)

    def parse_locations(self):
        location_tags = self.xmlelement.iterfind(self.namespaced("location"))
        locations = []
        last_location = None
        for location_tag in location_tags:
            location = location_tag.get("filename")
            line = location_tag.get("line")
            if line is not None and line.startswith(("+", "-")):
                # Relative locations
                if last_location is None and (
                    previous_unit := self.get_previous_unit()
                ):
                    last_location = previous_unit.get_last_location()

                offset = 0
                if last_location:
                    if not location:
                        location = last_location[0]
                    offset = last_location[1]
                line = offset + int(line)
            if location or line:
                last_location = (location, line)
                locations.append(last_location)
        self._locations = locations

    def get_last_location(self):
        if self._locations is None:
            self.parse_locations()

        if not self._locations:
            previous = self.get_previous_unit()
            if previous is None:
                return None
            return previous.get_last_location()

        return self._locations[-1]

    def get_previous_unit(self):
        found = None
        for pos, unit in enumerate(self._store.units):
            # Use is here to compare objects as __eq__ implementation in
            # LISAUnit might give unexpected results
            if unit is self:
                found = pos
                break
        if not found or found == 0:
            return None
        return self._store.units[found - 1]

    def getlocations(self):
        if self._locations is None:
            self.parse_locations()

        return [
            f"{location}{':' if location else ''}{line}"
            for location, line in self._locations
        ]

    def merge(self, otherunit, overwrite=False, comments=True, authoritative=False):
        super().merge(otherunit, overwrite, comments)
        # TODO: check if this is necessary:
        if otherunit.isfuzzy():
            self.markfuzzy()
        else:
            self.markfuzzy(False)

    def isobsolete(self):
        return self._gettype() in {"obsolete", "vanished"}

    def get_state_n(self):
        type = self._gettype()
        if type == "unfinished":
            # We want to distinguish between fuzzy and untranslated, which the
            # format doesn't really do
            if self.target:
                return self.S_FUZZY
            return self.S_UNTRANSLATED
        if type == "vanished":
            return self.S_OBSOLETE
        return self.statemap[type]

    def set_state_n(self, value):
        if value not in self.statemap_r:
            value = self.get_state_id(value)

        if value == self.S_UNTRANSLATED:
            # No real way of representing that in the format, so we just
            # handle it the same as unfinished
            value = self.S_FUZZY
        self._settype(self.statemap_r[value])


class tsfile(lisa.LISAfile):
    """Class representing a TS file store."""

    UnitClass = tsunit
    Name = "Qt Linguist Translation File"
    Mimetypes = ["application/x-linguist"]
    Extensions = ["ts"]
    rootNode = "TS"
    # We will switch out .body to fit with the context we are working on
    bodyNode = "context"
    XMLskeleton = """<!DOCTYPE TS>
<TS>
</TS>
"""
    XMLindent = {"indent": "    ", "skip": {"TS"}, "toplevel": False}
    # For conformance with Qt output, write XML declaration with double quotes
    XMLuppercaseEncoding = False
    namespace = ""

    def __init__(self, *args, **kwargs):
        self._contextname = None
        self.last_location = None
        super().__init__(*args, **kwargs)

    def initbody(self):
        """Initialises self.body."""
        self.namespace = self.document.getroot().nsmap.get(None, None)
        self.header = self.document.getroot()
        if self._contextname:
            self.body = self._getcontextnode(self._contextname)
        else:
            self.body = self.document.getroot()

    def getsourcelanguage(self):
        """
        Get the source language for this .ts file.

        The 'sourcelanguage' attribute was only added to the TS format in
        Qt v4.5. We return 'en' if there is no sourcelanguage set.

        We don't implement setsourcelanguage as users really shouldn't be
        altering the source language in .ts files, it should be set correctly
        by the extraction tools.

        :return: ISO code e.g. af, fr, pt_BR
        :rtype: String
        """
        lang = data.normalize_code(self.header.get("sourcelanguage", "en"))
        if lang == "en-us":
            return "en"
        return lang

    def gettargetlanguage(self):
        """
        Get the target language for this .ts file.

        :return: ISO code e.g. af, fr, pt_BR
        :rtype: String
        """
        return data.normalize_code(self.header.get("language"))

    def settargetlanguage(self, targetlanguage):
        """
        Set the target language for this .ts file to *targetlanguage*.

        :param targetlanguage: ISO code e.g. af, fr, pt_BR
        :type targetlanguage: String
        """
        if targetlanguage:
            self.header.set("language", targetlanguage)

    def _createcontext(self, contextname, comment=None):
        """Creates a context node with an optional comment."""
        context = etree.SubElement(
            self.document.getroot(), self.namespaced(self.bodyNode)
        )
        name = etree.SubElement(context, self.namespaced("name"))
        safely_set_text(name, contextname)
        if comment:
            comment_node = etree.SubElement(context, "comment")
            safely_set_text(comment_node, comment)
        return context

    def _getcontextname(self, contextnode):
        """Returns the name of the given context node."""
        return contextnode.find(self.namespaced("name")).text

    def _getcontextnames(self):
        """Returns all contextnames in this TS file."""
        contextnodes = self.document.findall(self.namespaced("context"))
        return [self.getcontextname(contextnode) for contextnode in contextnodes]

    def _getcontextnode(self, contextname):
        """Returns the context node with the given name."""
        contextnodes = self.document.findall(self.namespaced("context"))
        for contextnode in contextnodes:
            if self._getcontextname(contextnode) == contextname:
                return contextnode
        return None

    def addunit(
        self, unit, new=True, contextname=None, comment=None, createifmissing=True
    ):
        """
        Adds the given unit to the last used body node (current context).

        If the contextname is specified, switch to that context (creating it if
        allowed by createifmissing).
        """
        if contextname is None:
            contextname = unit.getcontextname()

        if self._contextname != contextname and not self._switchcontext(
            contextname, comment, createifmissing
        ):
            return None
        super().addunit(unit, new)
        #        lisa.setXMLspace(unit.xmlelement, "preserve")
        return unit

    def _switchcontext(self, contextname, comment, createifmissing=False):
        """
        Switch the current context to the one named contextname, optionally
        creating it if it doesn't exist.
        """
        self._contextname = contextname
        contextnode = self._getcontextnode(contextname)
        if contextnode is None:
            if not createifmissing:
                return False
            contextnode = self._createcontext(contextname, comment)

        self.body = contextnode
        return self.body is not None

    def nplural(self):
        code = self.header.get("language").lower().replace("-", "_").split("_")[0]
        if code in data.qt_plural_tags:
            return len(data.qt_plural_tags[code])
        lang = data.get_language(self.header.get("language"))
        if lang is None:
            return 1
        return lang[1]

    def serialize_hook(self, treestring: str) -> bytes:
        pos = 0
        out = []
        while pos >= 0:
            nextpos = treestring.find("<", pos)
            out.append(treestring[pos:nextpos].translate(OUTPUT_TRANS))
            pos = nextpos
            nextpos = treestring.find(">", pos)
            out.append(treestring[pos:nextpos])
            pos = nextpos
        out.append(treestring[pos:])
        return super().serialize_hook("".join(out))

    def serialize(self, out):
        """Write the XML document to a file."""
        root = self.document.getroot()
        for e in root.xpath(
            "//*[not(./node()) and not(text()) and not(name() = 'location')]"
        ):
            e.text = ""
        super().serialize(out)
