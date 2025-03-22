#
# Copyright 2005-2009 Zuza Software Foundation
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

"""module for parsing TMX translation memeory files."""

from lxml import etree

from translate import __version__
from translate.misc.xml_helpers import safely_set_text, setXMLlang
from translate.storage import lisa


class tmxunit(lisa.LISAunit):
    """A single unit in the TMX file."""

    rootNode = "tu"
    languageNode = "tuv"
    textNode = "seg"

    def createlanguageNode(self, lang, text, purpose):
        """Returns a langset xml Element setup with given parameters."""
        langset = etree.Element(self.languageNode)
        setXMLlang(langset, lang)
        seg = etree.SubElement(langset, self.textNode)
        # implied by the standard:
        # setXMLspace(seg, "preserve")
        safely_set_text(seg, text)

        return langset

    def getid(self):
        """
        Returns the identifier for this unit. The optional tuid property is
        used if available, otherwise we inherit .getid(). Note that the tuid
        property is only mandated to be unique from TMX 2.0.
        """
        id = self.xmlelement.get("tuid", "")
        return id or super().getid()

    def istranslatable(self):
        return bool(self.source)

    def addnote(self, text, origin=None, position="append"):
        """
        Add a note specifically in a "note" tag.

        The origin parameter is ignored
        """
        note = etree.SubElement(self.xmlelement, self.namespaced("note"))
        safely_set_text(note, text.strip())

    def _getnotelist(self, origin=None):
        """
        Returns the text from notes.

        :param origin: Ignored
        :return: The text from notes
        :rtype: List
        """
        note_nodes = self.xmlelement.iterdescendants(self.namespaced("note"))
        return [lisa.getText(note) for note in note_nodes]

    def getnotes(self, origin=None):
        return "\n".join(self._getnotelist(origin=origin))

    def removenotes(self, origin=None):
        """Remove all the translator notes."""
        notes = self.xmlelement.iterdescendants(self.namespaced("note"))
        for note in notes:
            self.xmlelement.remove(note)

    def adderror(self, errorname, errortext):
        """Adds an error message to this unit."""
        # TODO: consider factoring out: some duplication between XLIFF and TMX
        text = errorname
        if errortext:
            text += ": " + errortext
        self.addnote(text, origin="pofilter")

    def geterrors(self):
        """Get all error messages."""
        # TODO: consider factoring out: some duplication between XLIFF and TMX
        notelist = self._getnotelist(origin="pofilter")
        errordict = {}
        for note in notelist:
            errorname, errortext = note.split(": ")
            errordict[errorname] = errortext
        return errordict

    def copy(self):
        """
        Make a copy of the translation unit.

        We don't want to make a deep copy - this could duplicate the whole XML
        tree. For now we just serialise and reparse the unit's XML.
        """
        # TODO: check performance
        new_unit = self.__class__(None, empty=True)
        new_unit.xmlelement = etree.fromstring(etree.tostring(self.xmlelement))
        return new_unit


class tmxfile(lisa.LISAfile):
    """Class representing a TMX file store."""

    UnitClass = tmxunit
    Name = "TMX Translation Memory"
    Mimetypes = ["application/x-tmx"]
    Extensions = ["tmx"]
    rootNode = "tmx"
    bodyNode = "body"
    XMLskeleton = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
<header></header>
<body></body>
</tmx>"""

    def addheader(self):
        headernode = next(
            self.document.getroot().iterchildren(self.namespaced("header"))
        )
        headernode.set("creationtool", "Translate Toolkit")
        headernode.set("creationtoolversion", __version__.sver)
        headernode.set("segtype", "sentence")
        headernode.set("o-tmf", "UTF-8")
        headernode.set("adminlang", "en")
        # TODO: consider adminlang. Used for notes, etc. Possibly same as
        # targetlanguage
        headernode.set("srclang", self.sourcelanguage)
        headernode.set("datatype", "PlainText")
        # headernode.set("creationdate", "YYYYMMDDTHHMMSSZ"
        # headernode.set("creationid", "CodeSyntax"

    def addtranslation(self, source, srclang, translation, translang, comment=None):
        """Addtranslation method for testing old unit tests."""
        unit = self.addsourceunit(source)
        unit.target = translation
        if comment is not None and len(comment) > 0:
            unit.addnote(comment)

        tuvs = unit.xmlelement.iterdescendants(self.namespaced("tuv"))
        setXMLlang(next(tuvs), srclang)
        setXMLlang(next(tuvs), translang)

    def translate(self, sourcetext, sourcelang=None, targetlang=None):
        """Method to test old unit tests."""
        return getattr(self.findunit(sourcetext), "target", None)
