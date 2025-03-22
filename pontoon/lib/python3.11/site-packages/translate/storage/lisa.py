#
# Copyright 2006-2011 Zuza Software Foundation
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

"""Parent class for LISA standards (TMX, TBX, XLIFF)."""

import contextlib

from lxml import etree

from translate.misc.xml_helpers import (
    expand_closing_tags,
    getText,
    getXMLlang,
    getXMLspace,
    namespaced,
    reindent,
)
from translate.storage import base


class LISAunit(base.TranslationUnit):
    """
    A single unit in the file.  Provisional work is done to make several
    languages possible.
    """

    # The name of the root element of this unit type:(termEntry, tu, trans-unit)
    rootNode = ""
    # The name of the per language element of this unit type:(termEntry, tu,
    # trans-unit)
    languageNode = ""
    # The name of the innermost element of this unit type:(term, seg)
    textNode = ""

    namespace = None
    _default_xml_space = "preserve"
    """The default handling of spacing in the absense of an xml:space
    attribute.

    This is mostly for correcting XLIFF behaviour."""

    def __init__(self, source, empty=False, **kwargs):
        """Constructs a unit containing the given source string."""
        self._rich_source = None
        self._rich_target = None
        if empty:
            self._state_n = 0
            return
        self.xmlelement = etree.Element(self.namespaced(self.rootNode))
        # add descrip, note, etc.
        super().__init__(source)

    def __eq__(self, other):
        """Compares two units."""
        if not isinstance(other, LISAunit):
            return super().__eq__(other)
        languageNodes = self.getlanguageNodes()
        otherlanguageNodes = other.getlanguageNodes()
        if len(languageNodes) != len(otherlanguageNodes):
            return False
        for i in range(len(languageNodes)):
            mytext = self.getNodeText(
                languageNodes[i], getXMLspace(self.xmlelement, self._default_xml_space)
            )
            othertext = other.getNodeText(
                otherlanguageNodes[i],
                getXMLspace(self.xmlelement, self._default_xml_space),
            )
            if mytext != othertext:
                # TODO:^ maybe we want to take children and notes into account
                return False
        return True

    def namespaced(self, name):
        """
        Returns name in Clark notation.

        For example ``namespaced("source")`` in an XLIFF document
        might return::

            {urn:oasis:names:tc:xliff:document:1.1}source

        This is needed throughout lxml.
        """
        return namespaced(self.namespace, name)

    def set_source_dom(self, dom_node):
        languageNodes = self.getlanguageNodes()
        if len(languageNodes) > 0:
            self.xmlelement.replace(languageNodes[0], dom_node)
        else:
            self.xmlelement.append(dom_node)

    def get_source_dom(self):
        return self.getlanguageNode(lang=None, index=0)

    source_dom = property(get_source_dom, set_source_dom)

    @property
    def source(self):
        return self.getNodeText(
            self.source_dom, getXMLspace(self.xmlelement, self._default_xml_space)
        )

    @source.setter
    def source(self, source):
        self.setsource(source, sourcelang="en")

    def setsource(self, text, sourcelang="en"):
        self._rich_source = None
        self.source_dom = self.createlanguageNode(sourcelang, text, "source")

    def set_target_dom(self, dom_node, append=False):
        languageNodes = self.getlanguageNodes()
        if dom_node is not None:
            if append or len(languageNodes) == 0:
                self.xmlelement.append(dom_node)
            else:
                self.xmlelement.insert(1, dom_node)
        if not append and len(languageNodes) > 1:
            self.xmlelement.remove(languageNodes[1])

    def get_target_dom(self, lang=None):
        if lang:
            return self.getlanguageNode(lang=lang)
        return self.getlanguageNode(lang=None, index=1)

    target_dom = property(get_target_dom)

    def gettarget(self, lang=None):
        """
        retrieves the "target" text (second entry), or the entry in the
        specified language, if it exists.
        """
        return self.getNodeText(
            self.get_target_dom(lang),
            getXMLspace(self.xmlelement, self._default_xml_space),
        )

    def settarget(self, target, lang="xx", append=False):
        """
        Sets the "target" string (second language), or alternatively appends
        to the list.
        """
        # XXX: we really need the language - can't really be optional, and we
        # need to propagate it
        if self._rich_target is not None:
            self._rich_target = None
        # Firstly deal with reinitialising to None or setting to identical
        # string
        if self.target == target:
            return
        languageNode = self.target_dom
        if target is not None:
            if languageNode is None:
                languageNode = self.createlanguageNode(lang, target, "target")
                self.set_target_dom(languageNode, append)
            else:
                if self.textNode:
                    terms = languageNode.iter(self.namespaced(self.textNode))
                    with contextlib.suppress(StopIteration):
                        languageNode = next(terms)
                languageNode.text = target
        else:
            self.set_target_dom(None, False)

    @property
    def target(self):
        return self.gettarget()

    @target.setter
    def target(self, target):
        self.settarget(target)

    @staticmethod
    def createlanguageNode(lang, text, purpose=None):
        """
        Returns a xml Element setup with given parameters to represent a
        single language entry. Has to be overridden.
        """
        return

    def getlanguageNodes(self):
        """Returns a list of all nodes that contain per language information."""
        return list(self.xmlelement.iterchildren(self.namespaced(self.languageNode)))

    def getlanguageNode(self, lang=None, index=None):
        """Retrieves a :attr:`languageNode` either by language or by index."""
        if lang is None and index is None:
            raise KeyError("No criteria for languageNode given")
        languageNodes = self.getlanguageNodes()
        if lang:
            for set in languageNodes:
                if getXMLlang(set) == lang:
                    return set
        else:  # have to use index
            if index >= len(languageNodes):
                return None
            return languageNodes[index]
        return None

    def getNodeText(self, languageNode, xml_space="preserve"):
        """Retrieves the term from the given :attr:`languageNode`."""
        if languageNode is None:
            return None
        if self.textNode:
            terms = languageNode.iterdescendants(self.namespaced(self.textNode))
            if terms is None:
                return None
            node = next(terms, None)
            if node is not None:
                return getText(node, xml_space)
            # didn't have the structure we expected
            return None
        return getText(languageNode, xml_space)

    def __str__(self):
        # 'unicode' encoding keeps the unicode status of the output
        return etree.tostring(self.xmlelement, pretty_print=True, encoding="unicode")

    def _set_property(self, name, value):
        self.xmlelement.attrib[name] = value

    xid = property(
        lambda self: self.xmlelement.attrib[self.namespaced("xid")],
        lambda self, value: self._set_property(self.namespaced("xid"), value),
    )

    rid = property(
        lambda self: self.xmlelement.attrib[self.namespaced("rid")],
        lambda self, value: self._set_property(self.namespaced("rid"), value),
    )

    @classmethod
    def createfromxmlElement(cls, element):
        term = cls(None, empty=True)
        term.xmlelement = element
        return term


class LISAfile(base.TranslationStore):
    """A class representing a file store for one of the LISA file formats."""

    UnitClass = LISAunit
    # The root node of the XML document:
    rootNode = ""
    # The root node of the content section:
    bodyNode = ""
    # The XML skeleton to use for empty construction:
    XMLskeleton = ""
    XMLindent = {}
    XMLdoublequotes = True
    XMLdoctype = None
    XMLuppercaseEncoding = True
    # Determine how empty tags should be serialized (<note></note> or <note />)
    XMLSelfClosingTags = True

    namespace = None

    def __init__(
        self, inputfile=None, sourcelanguage="en", targetlanguage=None, **kwargs
    ):
        super().__init__(**kwargs)
        if inputfile is not None:
            self.parse(inputfile)
            assert self.document.getroot().tag == self.namespaced(self.rootNode)
        else:
            # We strip out newlines to ensure that spaces in the skeleton
            # doesn't interfere with the the pretty printing of lxml
            self.parse(self.XMLskeleton.replace("\n", "").encode("utf-8"))
            self.setsourcelanguage(sourcelanguage)
            self.settargetlanguage(targetlanguage)
            self.addheader()

    def addheader(self):
        """Method to be overridden to initialise headers, etc."""

    def namespaced(self, name):
        """
        Returns name in Clark notation.

        For example ``namespaced("source")`` in an XLIFF document
        might return::

            {urn:oasis:names:tc:xliff:document:1.1}source

        This is needed throughout lxml.
        """
        return namespaced(self.namespace, name)

    def initbody(self):
        """
        Initialises self.body so it never needs to be retrieved from the XML
        again.
        """
        self.namespace = self.document.getroot().nsmap.get(None, None)
        self.body = self.document.find(f".//{self.namespaced(self.bodyNode)}")

    def addsourceunit(self, source):
        """Adds and returns a new unit with the given string as first entry."""
        newunit = self.UnitClass(source)
        self.addunit(newunit)
        return newunit

    def addunit(self, unit, new=True):
        unit.namespace = self.namespace
        super().addunit(unit)
        if new:
            self.body.append(unit.xmlelement)

    def removeunit(self, unit):
        super().removeunit(unit)
        unit.xmlelement.getparent().remove(unit.xmlelement)

    def serialize_hook(self, treestring: str) -> bytes:
        return treestring.encode(self.encoding)

    def serialize(self, out):
        """Converts to a string containing the file's XML."""
        root = self.document.getroot()
        xml_quote_format = '"' if self.XMLdoublequotes else "'"
        xml_encoding = (
            self.encoding.upper()
            if self.XMLuppercaseEncoding
            else self.encoding.lower()
        )

        xml_declaration = f"<?xml version={xml_quote_format}1.0{xml_quote_format} encoding={xml_quote_format}{xml_encoding}{xml_quote_format}?>\n"

        out.write(self.serialize_hook(xml_declaration))

        if self.XMLindent:
            reindent(root, **self.XMLindent)

        if not self.XMLSelfClosingTags:
            expand_closing_tags(root)

        treestring = etree.tostring(
            self.document,
            pretty_print=not self.XMLindent,
            xml_declaration=False,
            encoding="unicode",
            doctype=self.XMLdoctype,
        )

        out.write(self.serialize_hook(treestring))

    def parse(self, xml):
        """Populates this object from the given xml string."""
        if not hasattr(self, "filename"):
            self.filename = getattr(xml, "name", "")
        if hasattr(xml, "read"):
            xml.seek(0)
            posrc = xml.read()
            xml = posrc
        parser = etree.XMLParser(strip_cdata=False, resolve_entities=False)
        self.document = etree.fromstring(xml, parser).getroottree()
        self.encoding = self.document.docinfo.encoding
        self.initbody()
        assert self.document.getroot().tag == self.namespaced(self.rootNode)
        for entry in self.document.getroot().iterdescendants(
            self.namespaced(self.UnitClass.rootNode)
        ):
            term = self.UnitClass.createfromxmlElement(entry)
            self.addunit(term, new=False)
