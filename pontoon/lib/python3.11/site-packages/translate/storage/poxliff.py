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

"""
XLIFF classes specifically suited for handling the PO representation in
XLIFF.

This way the API supports plurals as if it was a PO file, for example.
"""

import contextlib
import re

from lxml import etree

from translate.misc.multistring import multistring
from translate.misc.xml_helpers import setXMLspace
from translate.storage import base, lisa, poheader, xliff
from translate.storage.placeables import general

plural_id_re = re.compile(r".+\[[123456]\]$")


def hasplurals(thing):
    if not isinstance(thing, multistring):
        return False
    return len(thing.strings) > 1


class PoXliffUnit(xliff.xliffunit):
    """A class to specifically handle the plural units created from a po file."""

    rich_parsers = general.parsers

    def __init__(self, source=None, empty=False, **kwargs):
        self._rich_source = None
        self._rich_target = None
        self._state_n = 0
        self.units = []

        if empty:
            return

        if not hasplurals(source):
            super().__init__(source)
            return

        self.xmlelement = etree.Element(self.namespaced("group"))
        self.xmlelement.set("restype", "x-gettext-plurals")
        self.source = source

    def __eq__(self, other):
        if isinstance(other, PoXliffUnit):
            if len(self.units) != len(other.units):
                return False
            if not super().__eq__(other):
                return False
            for i in range(len(self.units) - 1):
                if not self.units[i + 1] == other.units[i + 1]:
                    return False
            return True
        if len(self.units) <= 1:
            if isinstance(other, lisa.LISAunit):
                return super().__eq__(other)
            return self.source == other.source and self.target == other.target
        return False

    # XXX: We don't return language nodes correctly at the moment
    #    def getlanguageNodes(self):
    #        if not self.hasplural():
    #            return super().getlanguageNodes()
    #        else:
    #            return self.units[0].getlanguageNodes()

    @property
    def source(self):
        if not self.hasplural():
            return super().source
        return multistring([unit.source for unit in self.units])

    @source.setter
    def source(self, source):
        self.setsource(source, sourcelang="en")

    def setsource(self, source, sourcelang="en"):
        # TODO: consider changing from plural to singular, etc.
        self._rich_source = None
        if not hasplurals(source):
            super().setsource(source, sourcelang)
        else:
            target = self.target
            for unit in self.units:
                with contextlib.suppress(ValueError):
                    self.xmlelement.remove(unit.xmlelement)
            self.units = []
            for s in source.strings:
                newunit = xliff.xliffunit(s)
                #                newunit.namespace = self.namespace #XXX?necessary?
                self.units.append(newunit)
                self.xmlelement.append(newunit.xmlelement)
            self.target = target

    # We don't support any rich strings yet
    multistring_to_rich = base.TranslationUnit.multistring_to_rich
    rich_to_multistring = base.TranslationUnit.rich_to_multistring

    rich_source = base.TranslationUnit.rich_source
    rich_target = base.TranslationUnit.rich_target

    def gettarget(self, lang=None):
        if self.hasplural():
            strings = [unit.target or "" for unit in self.units]
            if strings:
                return multistring(strings)
            return None
        return super().gettarget(lang)

    def settarget(self, target, lang="xx", append=False):
        self._rich_target = None
        if self.target == target:
            return
        if not self.hasplural():
            super().settarget(target, lang, append)
            return
        if not isinstance(target, multistring):
            target = multistring(target)
        source = self.source
        sourcel = len(source.strings)
        targetl = len(target.strings)
        if sourcel < targetl:
            sources = source.strings + [source.strings[-1]] * (targetl - sourcel)
            targets = target.strings
            id = self.getid()
            self.source = multistring(sources)
            self.setid(id)
        elif targetl < sourcel:
            targets = target.strings + [""] * (sourcel - targetl)
        else:
            targets = target.strings

        for i in range(len(self.units)):
            self.units[i].target = targets[i]

    def addnote(self, text, origin=None, position="append"):
        """Add a note specifically in a "note" tag."""
        note = etree.SubElement(self.xmlelement, self.namespaced("note"))
        note.text = text
        if origin:
            note.set("from", origin)
        for unit in self.units[1:]:
            unit.addnote(text, origin)

    def getnotes(self, origin=None):
        # NOTE: We support both <context> and <note> tags in xliff files for comments
        if origin == "translator":
            notes = super().getnotes("translator")
            trancomments = self.gettranslatorcomments()
            if notes == trancomments or trancomments.find(notes) >= 0:
                notes = ""
            elif notes.find(trancomments) >= 0:
                trancomments = notes
                notes = ""
            return trancomments + notes
        if origin in {"programmer", "developer", "source code"}:
            devcomments = super().getnotes("developer")
            autocomments = self.getautomaticcomments()
            if devcomments == autocomments or autocomments.find(devcomments) >= 0:
                devcomments = ""
            elif devcomments.find(autocomments) >= 0:
                autocomments = devcomments
                devcomments = ""
            return autocomments
        return super().getnotes(origin)

    def markfuzzy(self, value=True):
        super().markfuzzy(value)
        for unit in self.units[1:]:
            unit.markfuzzy(value)

    def marktranslated(self):
        super().marktranslated()
        for unit in self.units[1:]:
            unit.marktranslated()

    def setid(self, id):
        super().setid(id)
        if len(self.units) > 1:
            for i in range(len(self.units)):
                self.units[i].setid("%s[%d]" % (id, i))

    def getlocations(self):
        """Returns all the references (source locations)."""
        groups = self.getcontextgroups("po-reference")
        references = []
        for group in groups:
            sourcefile = ""
            linenumber = ""
            for type, text in group:
                if type == "sourcefile":
                    sourcefile = text
                elif type == "linenumber":
                    linenumber = text
            assert sourcefile
            if linenumber:
                sourcefile = sourcefile + ":" + linenumber
            references.append(sourcefile)
        return references

    def getautomaticcomments(self):
        """
        Returns the automatic comments (x-po-autocomment), which corresponds
        to the #. style po comments.
        """
        groups = self.getcontextgroups("po-entry")
        comments = [
            text
            for group in groups
            for ctype, text in group
            if ctype == "x-po-autocomment"
        ]
        return "\n".join(comments)

    def gettranslatorcomments(self):
        """
        Returns the translator comments (x-po-trancomment), which
        corresponds to the # style po comments.
        """
        groups = self.getcontextgroups("po-entry")
        comments = [
            text
            for group in groups
            for ctype, text in group
            if ctype == "x-po-trancomment"
        ]
        return "\n".join(comments)

    def isheader(self):
        return "gettext-domain-header" in (self.getrestype() or "")

    def istranslatable(self):
        return super().istranslatable() and not self.isheader()

    @classmethod
    def createfromxmlElement(cls, element, namespace=None):
        if element.tag.endswith("trans-unit"):
            object = cls(None, empty=True)
            object.xmlelement = element
            object.namespace = namespace
            return object
        assert element.tag.endswith("group")
        group = cls(None, empty=True)
        group.xmlelement = element
        group.namespace = namespace
        units = list(element.iterdescendants(group.namespaced("trans-unit")))
        for unit in units:
            subunit = xliff.xliffunit.createfromxmlElement(unit)
            subunit.namespace = namespace
            group.units.append(subunit)
        return group

    def hasplural(self):
        return self.xmlelement.tag == self.namespaced("group")


class PoXliffFile(xliff.xlifffile, poheader.poheader):
    """a file for the po variant of Xliff files."""

    UnitClass = PoXliffUnit

    def __init__(self, *args, **kwargs):
        if "sourcelanguage" not in kwargs:
            kwargs["sourcelanguage"] = "en-US"
        xliff.xlifffile.__init__(self, *args, **kwargs)

    def createfilenode(self, filename, sourcelanguage="en-US", datatype="po"):
        # Let's ignore the sourcelanguage parameter opting for the internal
        # one. PO files will probably be one language
        return super().createfilenode(
            filename, sourcelanguage=self.sourcelanguage, datatype="po"
        )

    def _insert_header(self, header):
        header.xmlelement.set("restype", "x-gettext-domain-header")
        header.xmlelement.set("approved", "no")
        setXMLspace(header.xmlelement, "preserve")
        self.addunit(header)

    def addheaderunit(self, target, filename):
        unit = self.addsourceunit(target, filename, True)
        unit.target = target
        unit.xmlelement.set("restype", "x-gettext-domain-header")
        unit.xmlelement.set("approved", "no")
        setXMLspace(unit.xmlelement, "preserve")
        return unit

    def parse(self, xml):
        """Populates this object from the given xml string."""
        # TODO: Make more robust

        def ispluralgroup(node):
            """Determines whether the xml node refers to a getttext plural."""
            return node.get("restype") == "x-gettext-plurals"

        def isnonpluralunit(node):
            """
            determindes whether the xml node contains a plural like id.

            We want to filter out all the plural nodes, except the very first
            one in each group.
            """
            return plural_id_re.match(node.get("id") or "") is None

        def pluralunits(pluralgroups):
            for pluralgroup in pluralgroups:
                yield self.UnitClass.createfromxmlElement(
                    pluralgroup, namespace=self.namespace
                )

        self.filename = getattr(xml, "name", "")
        if hasattr(xml, "read"):
            xml.seek(0)
            xmlsrc = xml.read()
            xml = xmlsrc
        parser = etree.XMLParser(resolve_entities=False)
        self.document = etree.fromstring(xml, parser).getroottree()
        self.initbody()
        root_node = self.document.getroot()
        assert root_node.tag == self.namespaced(self.rootNode)
        groups = root_node.iterdescendants(self.namespaced("group"))
        pluralgroups = filter(ispluralgroup, groups)
        termEntries = root_node.iterdescendants(
            self.namespaced(self.UnitClass.rootNode)
        )

        singularunits = list(filter(isnonpluralunit, termEntries))
        if len(singularunits) == 0:
            return
        pluralunit_iter = pluralunits(pluralgroups)
        nextplural = next(pluralunit_iter, None)

        for entry in singularunits:
            term = self.UnitClass.createfromxmlElement(entry, namespace=self.namespace)
            if nextplural and str(term.getid()) == (f"{nextplural.getid()}[0]"):
                self.addunit(nextplural, new=False)
                nextplural = next(pluralunit_iter, None)
            else:
                self.addunit(term, new=False)
