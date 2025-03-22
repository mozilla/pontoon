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
String processing utilities for extracting strings with various kinds of
delimiters.
"""

from __future__ import annotations

import html.entities
import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def find_all(searchin: str, substr: str) -> Iterable[int]:
    """
    Returns a list of locations where substr occurs in searchin locations
    are not allowed to overlap.
    """
    location = 0
    substr_len = len(substr)
    while (location := searchin.find(substr, location)) != -1:
        yield location
        location += substr_len


def extract(
    source, startdelim, enddelim, escape=None, startinstring=False, allowreentry=True
):
    """
    Extracts a doublequote-delimited string from a string, allowing for
    backslash-escaping returns tuple of (quoted string with quotes, still in
    string at end).
    """
    # Note that this returns the quote characters as well... even internally
    instring = startinstring
    enteredonce = False
    lenstart = len(startdelim)
    lenend = len(enddelim)
    startdelim_places = list(find_all(source, startdelim))
    if startdelim == enddelim:
        enddelim_places = startdelim_places.copy()
    else:
        enddelim_places = list(find_all(source, enddelim))
    if escape is not None:
        lenescape = len(escape)
        escape_places = list(find_all(source, escape))
        # Filter escaped escapes
        true_escape = False
        true_escape_places = []
        for escape_pos in escape_places:
            if escape_pos - lenescape in escape_places:
                true_escape = not true_escape
            else:
                true_escape = True
            if true_escape:
                true_escape_places.append(escape_pos)
        startdelim_places = [
            pos
            for pos in startdelim_places
            if pos - lenescape not in true_escape_places
        ]
        enddelim_places = [
            pos + lenend
            for pos in enddelim_places
            if pos - lenescape not in true_escape_places
        ]
    else:
        enddelim_places = [pos + lenend for pos in enddelim_places]
    # Get a unique sorted list of the significant places in the string
    significant_places = [0, *startdelim_places, *enddelim_places, len(source) - 1]
    significant_places.sort()
    extracted = ""
    lastpos = None
    for pos in significant_places:
        if instring and pos in enddelim_places:
            # Make sure that if startdelim == enddelim we don't get confused
            # and count the same string as start and end.
            if lastpos == pos - lenstart and lastpos in startdelim_places:
                continue
            extracted += source[lastpos:pos]
            instring = False
            lastpos = pos
        if (
            (not instring)
            and pos in startdelim_places
            and not (enteredonce and not allowreentry)
        ):
            instring = True
            enteredonce = True
            lastpos = pos
    if instring:
        extracted += source[lastpos:]
    return (extracted, instring)


def extractwithoutquotes(
    source,
    startdelim,
    enddelim,
    escape=None,
    startinstring=False,
    includeescapes=True,
    allowreentry=True,
):
    """
    Extracts a doublequote-delimited string from a string, allowing for
    backslash-escaping includeescapes can also be a function that takes the
    whole escaped string and returns the replaced version.
    """
    instring = startinstring
    enteredonce = False
    lenstart = len(startdelim)
    lenend = len(enddelim)
    startdelim_places = list(find_all(source, startdelim))
    if startdelim == enddelim:
        enddelim_places = startdelim_places.copy()
    else:
        enddelim_places = list(find_all(source, enddelim))
    # hell slow because it is called far too often
    if escape is not None:
        lenescape = len(escape)
        escape_places = list(find_all(source, escape))
        # filter escaped escapes
        true_escape = False
        true_escape_places = []
        for escape_pos in escape_places:
            if escape_pos - lenescape in escape_places:
                true_escape = not true_escape
            else:
                true_escape = True
            if true_escape:
                true_escape_places.append(escape_pos)
        startdelim_places = [
            pos
            for pos in startdelim_places
            if pos - lenescape not in true_escape_places
        ]
        enddelim_places = [
            pos + lenend
            for pos in enddelim_places
            if pos - lenescape not in true_escape_places
        ]
    else:
        enddelim_places = [pos + lenend for pos in enddelim_places]
    # get a unique sorted list of the significant places in the string
    significant_places = [0, *startdelim_places, *enddelim_places, len(source) - 1]
    significant_places.sort()
    extracted = ""
    lastpos = 0
    callable_includeescapes = callable(includeescapes)
    checkescapes = callable_includeescapes or not includeescapes
    for pos in significant_places:
        if instring and pos in enddelim_places and lastpos != pos - lenstart:
            section_start, section_end = lastpos + len(startdelim), pos - len(enddelim)
            section = source[section_start:section_end]
            if escape is not None and checkescapes:
                escape_list = [
                    epos - section_start
                    for epos in true_escape_places
                    if section_start <= epos <= section_end
                ]
                new_section = ""
                last_epos = 0
                for epos in escape_list:
                    new_section += section[last_epos:epos]
                    if callable_includeescapes:
                        replace_escape = includeescapes(
                            section[epos : epos + lenescape + 1]
                        )
                        # TODO: deprecate old method of returning boolean from
                        # includeescape, by removing this if block
                        if not isinstance(replace_escape, str):
                            if replace_escape:
                                replace_escape = section[epos : epos + lenescape + 1]
                            else:
                                replace_escape = section[
                                    epos + lenescape : epos + lenescape + 1
                                ]
                        new_section += replace_escape
                        last_epos = epos + lenescape + 1
                    else:
                        last_epos = epos + lenescape
                section = new_section + section[last_epos:]
            extracted += section
            instring = False
            lastpos = pos
        if (
            (not instring)
            and pos in startdelim_places
            and not (enteredonce and not allowreentry)
        ):
            instring = True
            enteredonce = True
            lastpos = pos
    if instring:
        section_start = lastpos + len(startdelim)
        section = source[section_start:]
        if escape is not None and not includeescapes:
            escape_list = [
                epos - section_start
                for epos in true_escape_places
                if section_start <= epos
            ]
            new_section = ""
            last_epos = 0
            for epos in escape_list:
                new_section += section[last_epos:epos]
                if callable_includeescapes and includeescapes(
                    section[epos : epos + lenescape + 1]
                ):
                    last_epos = epos
                else:
                    last_epos = epos + lenescape
            section = new_section + section[last_epos:]
        extracted += section
    return (extracted, instring)


# TODO: investigate if ord is needed
def _encode_entity_char(char: str, codepoint2name: dict[str, str]) -> str:
    charnum = ord(char)
    if charnum in codepoint2name:
        return f"&{codepoint2name[charnum]};"
    return char


def entityencode(source: str, codepoint2name: dict[str, str]) -> str:
    """
    Encode ``source`` using entities from ``codepoint2name``.

    :param unicode source: Source string to encode
    :param codepoint2name: Dictionary mapping code points to entity names
           (without the the leading ``&`` or the trailing ``;``)
    :type codepoint2name: :meth:`dict`
    """
    output = []
    inentity = False
    for char in source:
        if char == "&":
            inentity = True
            possibleentity = ""
            continue
        if inentity:
            if char == ";":
                output.append(f"&{possibleentity};")
                inentity = False
            elif char == " ":
                output.extend(
                    (
                        _encode_entity_char("&", codepoint2name),
                        entityencode(possibleentity + char, codepoint2name),
                    )
                )
                inentity = False
            else:
                possibleentity += char
        else:
            output.append(_encode_entity_char(char, codepoint2name))
    if inentity:
        # Handle nonentities at end of string.
        output.append(
            _encode_entity_char("&", codepoint2name)
            + entityencode(possibleentity, codepoint2name)
        )

    return "".join(output)


def _has_entity_end(source: str) -> bool:
    for char in source:
        if char == ";":
            return True
        if char == " ":
            return False
    return False


def entitydecode(source: str, name2codepoint: dict[str, str]) -> str:
    """
    Decode ``source`` using entities from ``name2codepoint``.

    :param unicode source: Source string to decode
    :param name2codepoint: Dictionary mapping entity names (without the
           the leading ``&`` or the trailing ``;``) to code points
    :type name2codepoint: :meth:`dict`
    """
    output = []
    inentity = False
    for i, char in enumerate(source):
        char = source[i]
        if char == "&":
            inentity = True
            possibleentity = ""
            continue
        if inentity:
            if char == ";":
                if len(possibleentity) > 0 and possibleentity in name2codepoint:
                    entchar = chr(name2codepoint[possibleentity])
                    if entchar == "&" and _has_entity_end(source[i + 1 :]):
                        output.append(f"&{possibleentity};")
                    else:
                        output.append(entchar)
                    inentity = False
                else:
                    output.append(f"&{possibleentity};")
                    inentity = False
            elif char == " ":
                output.append(f"&{possibleentity}{char}")
                inentity = False
            else:
                possibleentity += char
        else:
            output.append(char)
    if inentity:
        # Handle nonentities at end of string.
        output.append(f"&{possibleentity}")
    return "".join(output)


def htmlentityencode(source):
    """
    Encode ``source`` using HTML entities e.g. © -> ``&copy;``.

    :param unicode source: Source string to encode
    """
    return entityencode(source, html.entities.codepoint2name)


def htmlentitydecode(source: str) -> str:
    """
    Decode source using HTML entities e.g. ``&copy;`` -> ©.

    :param unicode source: Source string to decode
    """
    return entitydecode(source, html.entities.name2codepoint)


def javapropertiesencode(source: str) -> str:
    """
    Encodes source in the escaped-unicode encoding used by Java
    .properties files.
    """
    output = []
    if source and source[0] == " ":
        output.append("\\")
    for char in source:
        charnum = ord(char)
        if char in controlchars:
            output.append(controlchars[char])
        elif 0 <= charnum < 128:
            output.append(str(char))
        else:
            output.append(f"\\u{charnum:04X}")
    return "".join(output)


def java_utf8_properties_encode(source: str) -> str:
    """
    Encodes source in the escaped-unicode encoding used by java utf-8
    .properties files.
    """
    output = []
    for char in source:
        if char in controlchars:
            output.append(controlchars[char])
        else:
            output.append(char)
    return "".join(output)


def xwiki_properties_encode(source: str, encoding: str) -> str:
    if re.search(r"\{[0-9]+\}", source):
        source = source.replace("'", "''")
    if encoding == "utf-8":
        return java_utf8_properties_encode(source)
    return javapropertiesencode(source)


def escapespace(char: str) -> str:
    assert len(char) == 1
    if char.isspace():
        return f"\\u{ord(char):04X}"
    return char


def mozillaescapemarginspaces(source: str) -> str:
    """Escape leading and trailing spaces for Mozilla .properties files."""
    if not source:
        return ""
    if len(source) == 1:
        return escapespace(source)
    return escapespace(source[0]) + source[1:-1] + escapespace(source[-1])


propertyescapes = {
    # escapes that are self-escaping
    "\\": "\\",
    "'": "'",
    '"': '"',
    # control characters that we keep
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}

controlchars = {
    # complement of the above with all control chars
    "\\": r"\\",
    "\x00": r"\u0000",
    "\x01": r"\u0001",
    "\x02": r"\u0002",
    "\x03": r"\u0003",
    "\x04": r"\u0004",
    "\x05": r"\u0005",
    "\x06": r"\u0006",
    "\x07": r"\u0007",
    "\x08": r"\u0008",
    "\t": r"\t",
    "\n": r"\n",
    "\x0b": r"\u000b",
    "\f": r"\f",
    "\r": r"\r",
    "\x0e": r"\u000e",
    "\x0f": r"\u000f",
    "\x10": r"\u0010",
    "\x11": r"\u0011",
    "\x12": r"\u0012",
    "\x13": r"\u0013",
    "\x14": r"\u0014",
    "\x15": r"\u0015",
    "\x16": r"\u0016",
    "\x17": r"\u0017",
    "\x18": r"\u0018",
    "\x19": r"\u0019",
    "\x1a": r"\u001a",
    "\x1b": r"\u001b",
    "\x1c": r"\u001c",
    "\x1d": r"\u001d",
    "\x1e": r"\u001e",
    "\x1f": r"\u001f",
}
controlchars_trans = str.maketrans(controlchars)


def escapecontrols(source: str) -> str:
    """Escape control characters in the given string."""
    return source.translate(controlchars_trans)


def propertiesdecode(source: str) -> str:
    """
    Decodes source from the escaped-unicode encoding used by .properties
    files.

    Java uses Latin1 by default, and Mozilla uses UTF-8 by default.

    Since the .decode("unicode-escape") routine decodes everything, and we
    don't want to we reimplemented the algorithm from Python Objects/unicode.c
    in Python and modify it to retain escaped control characters.
    """
    output = []
    s = 0

    def unichr2(i):
        """
        Returns a Unicode string of one character with ordinal 32 <= i,
        otherwise an escaped control character.
        """
        if i >= 32:
            return chr(i)
        if chr(i) in controlchars:
            # we just return the character, unescaped
            # if people want to escape them they can use escapecontrols
            return chr(i)
        return f"\\u{i:04x}"

    while s < len(source):
        c = source[s]
        if c != "\\":
            output.append(c)
            s += 1
            continue
        s += 1
        if s >= len(source):
            # this is an escape at the end of the line, which implies
            # a continuation..., return the escape to inform the parser
            output.append(c)
            continue
        c = source[s]
        s += 1
        if c == "\n":
            pass
        # propertyescapes lookups
        elif c in propertyescapes:
            output.append(propertyescapes[c])
        # \uXXXX escapes
        # \UXXXX escapes
        elif c in "uU":
            digits = 4
            x = 0
            for digit in range(digits):
                if s + digit >= len(source):
                    digits = digit
                    break
                c = source[s + digit].lower()
                if c.isdigit() or c in "abcdef":
                    x <<= 4
                    if c.isdigit():
                        x += ord(c) - ord("0")
                    else:
                        x += ord(c) - ord("a") + 10
                else:
                    digits = digit
                    break
            s += digits
            output.append(unichr2(x))
        elif c == "N":
            if source[s] != "{":
                logging.warning("Invalid named unicode escape: no { after \\N")
                output.append(f"\\{c}")
                continue
            s += 1
            e = source.find("}", s)
            if e == -1:
                logging.warning("Invalid named unicode escape: no } after \\N{")
                output.append(f"\\{c}")
                continue
            import unicodedata

            name = source[s:e]
            output.append(unicodedata.lookup(name))
            s = e + 1
        else:
            output.append(c)  # Drop any \ that we don't specifically handle
    return "".join(output)


def xwiki_properties_decode(source: str) -> str:
    if re.search(r"\{[0-9]+\}", source):
        source = source.replace("''", "'")
    return propertiesdecode(source)


def findend(string: str, substring: str) -> int:
    s = string.find(substring)
    if s != -1:
        s += len(substring)
    return s


def rstripeol(string: str) -> str:
    return string.rstrip("\r\n")


def stripcomment(
    comment: str, startstring: str = "<!--", endstring: str = "-->"
) -> str:
    cstart = comment.find(startstring)
    if cstart == -1:
        cstart = 0
    else:
        cstart += len(startstring)
    cend = comment.find(endstring, cstart)
    return comment[cstart:cend].strip()


def unstripcomment(
    comment: str, startstring: str = "<!-- ", endstring: str = " -->\n"
) -> str:
    return startstring + comment.strip() + endstring
