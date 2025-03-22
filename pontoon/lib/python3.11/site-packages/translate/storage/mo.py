#
# Copyright 2007 Zuza Software Foundation
#
# the function "serialize" was derived from Python v2.4
#       (Tools/i18n/msgfmt.py - function "generate"):
#   Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>
#   Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Python Software Foundation.
#   All rights reserved.
#   original license: Python Software Foundation (version 2)
#
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
#

"""
Module for parsing Gettext .mo files for translation.

The coding of .mo files was produced from `Gettext documentation
<http://www.gnu.org/software/gettext/manual/gettext.html#MO-Files>`_,
Pythons msgfmt.py and by observing and testing existing .mo files in the wild.

The hash algorithm is implemented for MO files, this should result in
faster access of the MO file.  The hash is optional for Gettext
and is not needed for reading or writing MO files, in this implementation
it is always on and does produce sometimes different results to Gettext
in very small files.
"""

import array
import re
import struct

from translate.misc.multistring import multistring
from translate.storage import base, poheader

MO_MAGIC_NUMBER = 0x950412DE
POT_HEADER = re.compile(r"^POT-Creation-Date:.*(\n|$)", re.IGNORECASE | re.MULTILINE)


def mounpack(filename="messages.mo"):
    """Helper to unpack Gettext MO files into a Python string."""
    with open(filename, "rb") as fh:
        s = fh.read()
        return "\\x%02x" * len(s) % tuple(map(ord, s))


def my_swap4(result):
    c0 = (result >> 0) & 0xFF
    c1 = (result >> 8) & 0xFF
    c2 = (result >> 16) & 0xFF
    c3 = (result >> 24) & 0xFF

    return (c0 << 24) | (c1 << 16) | (c2 << 8) | c3


def hashpjw(str_param):
    HASHWORDBITS = 32
    hval = 0
    for s in str_param:
        if not s:
            break
        hval <<= 4
        hval += s
        g = hval & 0xF << (HASHWORDBITS - 4)
        if g != 0:
            hval ^= g >> HASHWORDBITS - 8
            hval ^= g
    return hval


def get_next_prime_number(start):
    # find the smallest prime number that is greater or equal "start"
    # this is based on hash lib implementation in gettext

    def is_prime(num):
        # No even number and none less than 10 will be passed here
        divn = 3
        sq = divn * divn

        while sq < num and num % divn != 0:
            divn += 1
            sq += 4 * divn
            divn += 1

        return num % divn != 0

    # Make it definitely odd
    candidate = start | 1

    while not is_prime(candidate):
        candidate += 2

    return candidate


class mounit(base.TranslationUnit):
    """A class representing a .mo translation message."""

    def __init__(self, source=None, **kwargs):
        self.msgctxt = []
        self.msgidcomments = []
        super().__init__(source)

    def getcontext(self):
        """Get the message context."""
        # Still need to handle KDE comments
        if self.msgctxt is None:
            return None
        return "".join(self.msgctxt)

    def setcontext(self, context):
        self.msgctxt = [context]

    def isheader(self):
        """Is this a header entry?."""
        return not self.source

    def istranslatable(self):
        """Is this message translateable?."""
        return bool(self.source)


class mofile(poheader.poheader, base.TranslationStore):
    """A class representing a .mo file."""

    UnitClass = mounit
    Name = "Gettext MO file"
    Mimetypes = ["application/x-gettext-catalog", "application/x-mo"]
    Extensions = ["mo", "gmo"]
    _binary = True

    def __init__(self, inputfile=None, **kwargs):
        super().__init__(**kwargs)
        self.filename = ""
        if inputfile is not None:
            self.parsestring(inputfile)

    def serialize(self, out):
        """Output a string representation of the MO data file."""
        # check the header of this file for the copyright note of this function

        def add_to_hash_table(string, i):
            hash_value = hashpjw(string)
            hash_cursor = hash_value % hash_size
            increment = 1 + (hash_value % (hash_size - 2))
            while hash_table[hash_cursor] != 0:
                hash_cursor += increment
                hash_cursor %= hash_size
            hash_table[hash_cursor] = i + 1

        def lst_encode(lst, join_char=b""):
            return join_char.join([i.encode("utf-8") for i in lst])

        # hash_size should be the smallest prime number that is greater
        # or equal (4 / 3 * N) - where N is the number of keys/units.
        # see gettext-0.17:gettext-tools/src/write-mo.c:406
        hash_size = get_next_prime_number((len(self.units) * 4) // 3)
        if hash_size <= 2:
            hash_size = 3
        MESSAGES = {}
        for unit in self.units:
            # If the unit is not translated, we should rather omit it entirely
            if not unit.istranslated():
                continue
            if isinstance(unit.source, multistring):
                source = lst_encode(unit.msgidcomments) + lst_encode(
                    unit.source.strings, b"\0"
                )
            else:
                source = lst_encode(unit.msgidcomments) + unit.source.encode("utf-8")
            if unit.msgctxt:
                source = lst_encode(unit.msgctxt) + b"\x04" + source
            if isinstance(unit.target, multistring):
                target = lst_encode(unit.target.strings, b"\0")
            elif unit.isheader():
                # Support for "reproducible builds": Delete information that
                # may vary between builds in the same conditions.
                target = POT_HEADER.sub("", unit.target).encode("utf-8")
            else:
                target = unit.target.encode("utf-8")
            if unit.target:
                MESSAGES[source] = target
        # using "I" works for 32- and 64-bit systems, but not for 16-bit!
        hash_table = array.array("I", [0] * hash_size)
        # the keys are sorted in the .mo file
        keys = sorted(MESSAGES.keys())
        offsets = []
        ids = strs = b""
        for i, id in enumerate(keys):
            # For each string, we need size and file offset.  Each string is
            # NUL terminated; the NUL does not count into the size.
            # TODO: We don't do any encoding detection from the PO Header
            add_to_hash_table(id, i)
            string = MESSAGES[id]  # id already encoded for use as dictionary key
            offsets.append((len(ids), len(id), len(strs), len(string)))
            ids = ids + id + b"\0"
            strs = strs + string + b"\0"
        # The header is 7 32-bit unsigned integers
        keystart = 7 * 4 + 16 * len(keys) + hash_size * 4
        # and the values start after the keys
        valuestart = keystart + len(ids)
        koffsets = []
        voffsets = []
        # The string table first has the list of keys, then the list of values.
        # Each entry has first the size of the string, then the file offset.
        for o1, l1, o2, l2 in offsets:
            koffsets = [*koffsets, l1, o1 + keystart]
            voffsets = [*voffsets, l2, o2 + valuestart]
        offsets = koffsets + voffsets
        out.write(
            struct.pack(
                "Iiiiiii",
                MO_MAGIC_NUMBER,  # Magic
                0,  # Version
                len(keys),  # # of entries
                7 * 4,  # start of key index
                7 * 4 + len(keys) * 8,  # start of value index
                hash_size,  # size of hash table
                7 * 4 + 2 * (len(keys) * 8),  # offset of hash table
            )
        )
        # additional data is not necessary for empty mo files
        if len(keys) > 0:
            out.write(array.array("i", offsets).tobytes())
            out.write(hash_table.tobytes())
            out.write(ids)
            out.write(strs)

    def parse(self, input):
        """Parses the given file or file source string."""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            mosrc = input.read()
            input.close()
            input = mosrc
        (little,) = struct.unpack("<L", input[:4])
        (big,) = struct.unpack(">L", input[:4])
        if little == MO_MAGIC_NUMBER:
            endian = "<"
        elif big == MO_MAGIC_NUMBER:
            endian = ">"
        else:
            raise ValueError("This is not an MO file")
        (
            _magic,
            version_maj,
            version_min,
            lenkeys,
            startkey,
            startvalue,
            _sizehash,
            _offsethash,
        ) = struct.unpack(f"{endian}LHHiiiii", input[: (7 * 4)])
        if version_maj >= 1:
            raise base.ParseError(
                """Unable to process version %d.%d MO files"""
                % (version_maj, version_min)
            )
        for i in range(lenkeys):
            nextkey = startkey + (i * 2 * 4)
            nextvalue = startvalue + (i * 2 * 4)
            klength, koffset = struct.unpack(
                f"{endian}ii", input[nextkey : nextkey + (2 * 4)]
            )
            vlength, voffset = struct.unpack(
                f"{endian}ii", input[nextvalue : nextvalue + (2 * 4)]
            )
            source = input[koffset : koffset + klength]
            context = None
            if b"\x04" in source:
                context, source = source.split(b"\x04")
            # Still need to handle KDE comments
            if not source:
                charset = re.search(
                    b"charset=([^\\s]+)", input[voffset : voffset + vlength]
                )
                if charset:
                    self.encoding = charset.group(1).decode()
            source = multistring([s.decode(self.encoding) for s in source.split(b"\0")])
            target = multistring(
                [
                    s.decode(self.encoding)
                    for s in input[voffset : voffset + vlength].split(b"\0")
                ]
            )
            newunit = mounit(source)
            newunit.target = target
            if context is not None:
                newunit.msgctxt.append(context.decode(self.encoding))
            self.addunit(newunit)
