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

"""Helper functions for working with XML."""

from __future__ import annotations

import re

from lxml import etree

# some useful xpath expressions
xml_preserve_ancestors = etree.XPath(
    "ancestor-or-self::*[attribute::xml:space='preserve']"
)
"""All ancestors with xml:space='preserve'"""

xml_space_ancestors = etree.XPath("ancestor-or-self::*/attribute::xml:space")
"""All xml:space attributes in the ancestors"""

string_xpath = etree.XPath("string()")
"""Return a non-normalized string in the node subtree"""

string_xpath_normalized = etree.XPath("normalize-space()")
"""Return a (space) normalized string in the node subtree"""


def getText(node, xml_space="preserve"):
    """
    Extracts the plain text content out of the given node.

    This method checks the xml:space attribute of the given node, and takes an
    optional default to use in case nothing is specified in this node.
    """
    xml_space = getXMLspace(node, xml_space)
    if xml_space == "default":
        return str(string_xpath_normalized(node))  # specific to lxml.etree
    return str(string_xpath(node))  # specific to lxml.etree

    # If we want to normalise space and only preserve it when the directive
    # xml:space="preserve" is given in node or in parents, consider this code:
    # xml_preserves = xml_preserve_ancestors(node)
    # if xml_preserves and xml_preserves[-1] == "preserve":
    #    return unicode(string_xpath(node)) # specific to lxml.etree
    # else:
    #    return unicode(string_xpath_normalized(node)) # specific to lxml.etree


XML_NS = "http://www.w3.org/XML/1998/namespace"


def getXMLlang(node):
    """Gets the xml:lang attribute on node."""
    return node.get(f"{{{XML_NS}}}lang")


def setXMLlang(node, lang):
    """Sets the xml:lang attribute on node."""
    node.set(f"{{{XML_NS}}}lang", lang)


def getXMLspace(node, default=None):
    """Gets the xml:space attribute on node."""
    value = node.get(f"{{{XML_NS}}}space")
    if value is None:
        return default
    return value


def setXMLspace(node, value):
    """Sets the xml:space attribute on node."""
    node.set(f"{{{XML_NS}}}space", value)


def namespaced(namespace, name):
    """
    Returns name in Clark notation within the given namespace.

    For example namespaced("source") in an XLIFF document might return::

      {urn:oasis:names:tc:xliff:document:1.1}source

    This is needed throughout lxml.
    """
    if namespace:
        return f"{{{namespace}}}{name}"
    return name


MULTIWHITESPACE_PATTERN = r"[\n\r\t ]+"
MULTIWHITESPACE_RE = re.compile(MULTIWHITESPACE_PATTERN, re.MULTILINE)


def normalize_space(text: str):
    """Normalize the given text for implementation of ``xml:space="default"``."""
    return MULTIWHITESPACE_RE.sub(" ", text)


def normalize_xml_space(node, xml_space: str, remove_start: bool = False):
    """
    normalize spaces following the nodes xml:space, or alternatively the
    given xml_space parameter.
    """
    xml_space = getXMLspace(node) or xml_space
    if xml_space == "preserve":
        return
    if node.text:
        node.text = normalize_space(node.text)
        if remove_start and node.text[0] == " ":
            node.text = node.text.lstrip()
            remove_start = False
        if len(node.text) > 0 and node.text.endswith(" "):
            remove_start = True
        if len(node) == 0:
            node.text = node.text.rstrip()
    if node.tail:
        node.tail = normalize_space(node.tail)

    for child in node:
        normalize_xml_space(child, remove_start)


def reindent(
    elem,
    level: int = 0,
    indent: str = "  ",
    max_level: int = 4,
    skip: set[str] | None = None,
    toplevel=True,
    leaves: set[str] | None = None,
    *,
    ignore_preserve: set[str] | None = None,
):
    """
    Adjust indentation to match specification.

    Each nested tag is identified by indent string, up to
    max_level depth, possibly skipping tags listed in skip.
    """
    if ignore_preserve is None:
        ignore_preserve = set()
    if skip is None:
        skip = set()
    if leaves is None:
        leaves = set()
    if elem.tag is etree.Entity or elem.tag is etree.Comment:
        return
    # Strip possible namespace from tag
    tag_name = elem.tag.split("}", 1)[-1]

    i = "\n" + (indent * level)
    if tag_name in skip:
        next_level = level
        extra_i = i
    else:
        next_level = level + 1
        extra_i = i + indent
    if level < max_level:
        is_leave = tag_name in leaves

        if (
            (not elem.text or not elem.text.strip())
            and (getXMLspace(elem) != "preserve" or tag_name in ignore_preserve)
            and len(elem)
            and elem[0].tag is not etree.Entity
            and not is_leave
        ):
            elem.text = extra_i
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        if not is_leave and len(elem):
            for child in elem:
                reindent(
                    elem=child,
                    level=next_level,
                    indent=indent,
                    max_level=max_level,
                    skip=skip,
                    toplevel=False,
                    leaves=leaves,
                    ignore_preserve=ignore_preserve,
                )

            # Adjust last element
            child = elem[-1]
            if (
                not child.tail or not child.tail.strip()
            ) and child.tag is not etree.Entity:
                child.tail = i
    if toplevel:
        if not elem.tail or not elem.tail.strip():
            elem.tail = ""
    elif not elem.tail or not elem.tail.strip():
        elem.tail = i


def expand_closing_tags(elem):
    """
    Changes value of empty XML tags to empty string.

    This changes lxml behavior to render these tags as
    <tag></tag> instead of <tag />
    """
    elements = [elem]
    while elements:
        elem = elements.pop()
        if elem.tag is etree.Entity:
            continue
        if elem.text is None:
            elem.text = ""
        elements.extend(elem)


"""
Characters which will get rejected by lxml, based on
https://github.com/lxml/lxml/blob/3ccc7d583e325ceb0ebdf8fc295bbb7fc8cd404d/src/lxml/apihelpers.pxi#L1474-L1503
and
https://github.com/GNOME/libxml2/blob/723b4de04015c5acccd3cda5dd60db7d00702064/include/libxml/chvalid.h#L108-L110
"""
XML_INVALID_CHARS_TRANS = str.maketrans(
    dict.fromkeys(
        (
            "\x00",  # Unicode Character 'NULL' (U+0000)
            "\x01",  # Unicode Character 'START OF HEADING' (U+0001)
            "\x02",  # Unicode Character 'START OF TEXT' (U+0002)
            "\x03",  # Unicode Character 'END OF TEXT' (U+0003)
            "\x04",  # Unicode Character 'END OF TRANSMISSION' (U+0004)
            "\x05",  # Unicode Character 'ENQUIRY' (U+0005)
            "\x06",  # Unicode Character 'ACKNOWLEDGE' (U+0006)
            "\x07",  # Unicode Character 'BELL' (U+0007), "\a" in Python
            "\x08",  # Unicode Character 'BACKSPACE' (U+0008), "\b" in Python
            "\x0b",  # Unicode Character 'LINE TABULATION' (U+000B), "\v" in Python
            "\x0c",  # Unicode Character 'FORM FEED (FF)' (U+000C), "\f" in Python
            "\x0e",  # Unicode Character 'SHIFT OUT' (U+000E)
            "\x0f",  # Unicode Character 'SHIFT IN' (U+000F)
            "\x10",  # Unicode Character 'DATA LINK ESCAPE' (U+0010)
            "\x11",  # Unicode Character 'DEVICE CONTROL ONE' (U+0011)
            "\x12",  # Unicode Character 'DEVICE CONTROL TWO' (U+0012)
            "\x13",  # Unicode Character 'DEVICE CONTROL THREE' (U+0013)
            "\x14",  # Unicode Character 'DEVICE CONTROL FOUR' (U+0014)
            "\x15",  # Unicode Character 'NEGATIVE ACKNOWLEDGE' (U+0015)
            "\x16",  # Unicode Character 'SYNCHRONOUS IDLE' (U+0016)
            "\x17",  # Unicode Character 'END OF TRANSMISSION BLOCK' (U+0017)
            "\x18",  # Unicode Character 'CANCEL' (U+0018)
            "\x19",  # Unicode Character 'END OF MEDIUM' (U+0019)
            "\x1a",  # Unicode Character 'SUBSTITUTE' (U+001A)
            "\x1b",  # Unicode Character 'ESCAPE' (U+001B)
            "\x1c",  # Unicode Character 'INFORMATION SEPARATOR FOUR' (U+001C)
            "\x1d",  # Unicode Character 'INFORMATION SEPARATOR THREE' (U+001D)
            "\x1e",  # Unicode Character 'INFORMATION SEPARATOR TWO' (U+001E)
            "\x1f",  # Unicode Character 'INFORMATION SEPARATOR ONE' (U+001F)
            "\ufffe",  # Invalid character
            "\uffff",  # Invalid character
            *(chr(x) for x in range(0xD800, 0xDFFF + 1)),
        )
    )
)


def valid_chars_only(text: str) -> str:
    """Prevent to crash libxml with unexpected chars."""
    return text.translate(XML_INVALID_CHARS_TRANS)


def safely_set_text(node, text: str) -> None:
    """
    Safe updating of ElementTree text of a node.

    In case of ValueError it strips any characters refused by lxml.
    """
    try:
        node.text = text
    except ValueError:
        # Prevents "All strings must be XML compatible" when string contains a control characters
        node.text = valid_chars_only(text)


def clear_content(node):
    """
    Removes XML node content.

    Unlike clear() this is not removing attributes.
    """
    for child in node.iterchildren(reversed=True):
        node.remove(child)
    node.text = None
