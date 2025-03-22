#
# Copyright 2002-2007 Zuza Software Foundation
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
Classes that hold units of .po files (pounit) or entire files (pofile).

Gettext-style .po (or .pot) files are used in translations for KDE, GNOME and
many other projects.

This uses libgettextpo from the gettext package. Any version before 0.17 will
at least cause some subtle bugs or may not work at all. Developers might want
to have a look at gettext-tools/libgettextpo/gettext-po.h from the gettext
package for the public API of the library.
"""

import ctypes.util
import logging
import os
import re
import sys
import tempfile
import threading
from ctypes import (
    CFUNCTYPE,
    POINTER,
    Structure,
    c_char_p,
    c_int,
    c_long,
    c_size_t,
    c_uint,
    cdll,
)

from translate.misc.multistring import multistring
from translate.storage import base, pocommon, pypo

logger = logging.getLogger(__name__)

lsep = " "
"""Separator for #: entries"""

STRING = c_char_p


# Structures
class po_message(Structure):
    pass


class po_file(Structure):
    pass


class po_filepos(Structure):
    pass


class po_iterator(Structure):
    pass


po_message_t = POINTER(po_message)
"""A po_message_t represents a message in a PO file."""

po_file_t = POINTER(po_file)
"""A po_file_t represents a PO file."""

po_filepos_t = POINTER(po_filepos)
"""A po_filepos_t represents the position in a PO file."""

po_iterator_t = POINTER(po_iterator)
"""A po_iterator_t represents an iterator through a PO file."""


# Function prototypes
xerror_prototype = CFUNCTYPE(
    None, c_int, po_message_t, STRING, c_uint, c_uint, c_int, STRING
)
xerror2_prototype = CFUNCTYPE(
    None,
    c_int,
    po_message_t,
    STRING,
    c_uint,
    c_uint,
    c_int,
    STRING,
    po_message_t,
    STRING,
    c_uint,
    c_uint,
    c_int,
    STRING,
)


# Structures (error handler)
class po_xerror_handler(Structure):
    _fields_ = [("xerror", xerror_prototype), ("xerror2", xerror2_prototype)]


class po_error_handler(Structure):
    _fields_ = [
        ("error", CFUNCTYPE(None, c_int, c_int, STRING)),
        ("error_at_line", CFUNCTYPE(None, c_int, c_int, STRING, c_uint, STRING)),
        ("multiline_warning", CFUNCTYPE(None, STRING, STRING)),
        ("multiline_error", CFUNCTYPE(None, STRING, STRING)),
    ]


xerror_storage = threading.local()

ignored_erorrs = {
    # TODO: this is probably bug somewhere in cpo, but
    # it used to be silently ignored before the exceptions
    # were raised, so it is left to fixing separately
    "invalid multibyte sequence",
    # Duplicate messages are allowed
    "duplicate message definition",
}


def trigger_exception(severity, filename, lineno, column, message_text):
    # Severity 0 is warning, severity 1 error, severity 2 critical
    if severity >= 1 and message_text not in ignored_erorrs:
        if filename:
            detail = f"{filename}:{lineno}:{column}: {message_text}"
        else:
            detail = message_text
        xerror_storage.exception = ValueError(detail)


# Callback functions for po_xerror_handler
def xerror_cb(severity, message, filename, lineno, column, multiline_p, message_text):
    message_text = message_text.decode()
    if filename:
        filename = filename.decode()
    logger.error(
        "xerror_cb %s %s %s %s %s %s %s",
        severity,
        message,
        filename,
        lineno,
        column,
        multiline_p,
        message_text,
    )
    trigger_exception(severity, filename, lineno, column, message_text)


def xerror2_cb(
    severity,
    message1,
    filename1,
    lineno1,
    column1,
    multiline_p1,
    message_text1,
    message2,
    filename2,
    lineno2,
    column2,
    multiline_p2,
    message_text2,
):
    message_text1 = message_text1.decode()
    message_text2 = message_text2.decode()
    if filename1:
        filename1 = filename1.decode()
    if filename2:
        filename2 = filename2.decode()
    logger.error(
        "xerror2_cb %s %s %s %s %s %s %s %s %s %s %s %s",
        severity,
        message1,
        filename1,
        lineno1,
        column1,
        multiline_p1,
        message_text1,
        filename2,
        lineno2,
        column2,
        multiline_p2,
        message_text2,
    )
    trigger_exception(severity, filename1, lineno1, column1, message_text1)


# Setup return and parameter types
# See also http://git.savannah.gnu.org/cgit/gettext.git/tree/gettext-tools/libgettextpo/gettext-po.in.h
def setup_call_types(gpo):
    # File access
    gpo.po_file_create.restype = po_file_t
    gpo.po_file_read_v3.argtypes = [STRING, POINTER(po_xerror_handler)]
    gpo.po_file_read_v3.restype = po_file_t
    gpo.po_file_write_v2.argtypes = [po_file_t, STRING, POINTER(po_xerror_handler)]
    gpo.po_file_write_v2.restype = po_file_t
    gpo.po_file_free.argtypes = [po_file_t]

    # Header
    gpo.po_file_domain_header.argtypes = [po_file_t, STRING]
    gpo.po_file_domain_header.restype = STRING
    gpo.po_header_field.argtypes = [STRING, STRING]
    gpo.po_header_field.restype = STRING
    gpo.po_header_set_field.argtypes = [STRING, STRING, STRING]
    gpo.po_header_set_field.restype = STRING

    # Locations (filepos)
    gpo.po_filepos_file.argtypes = [po_filepos_t]
    gpo.po_filepos_file.restype = STRING
    gpo.po_filepos_start_line.argtypes = [po_filepos_t]
    gpo.po_filepos_start_line.restype = c_int  # not strictly true casting
    gpo.po_message_filepos.argtypes = [po_message_t, c_int]
    gpo.po_message_filepos.restype = po_filepos_t
    gpo.po_message_add_filepos.argtypes = [po_message_t, STRING, c_size_t]
    gpo.po_message_remove_filepos.argtypes = [po_message_t, c_size_t]

    # Iterators
    gpo.po_message_iterator.argtypes = [po_file_t, STRING]
    gpo.po_message_iterator.restype = po_iterator_t
    gpo.po_message_iterator_free.argtypes = [po_iterator_t]
    gpo.po_next_message.argtypes = [po_iterator_t]
    gpo.po_next_message.restype = po_message_t
    gpo.po_message_insert.argtypes = [po_iterator_t, po_message_t]

    # Message (get methods)
    gpo.po_message_create.restype = po_message_t
    gpo.po_message_msgctxt.argtypes = [po_message_t]
    gpo.po_message_msgctxt.restype = STRING
    gpo.po_message_comments.argtypes = [po_message_t]
    gpo.po_message_comments.restype = STRING
    gpo.po_message_extracted_comments.argtypes = [po_message_t]
    gpo.po_message_extracted_comments.restype = STRING
    gpo.po_message_prev_msgctxt.argtypes = [po_message_t]
    gpo.po_message_prev_msgctxt.restype = STRING
    gpo.po_message_prev_msgid.argtypes = [po_message_t]
    gpo.po_message_prev_msgid.restype = STRING
    gpo.po_message_prev_msgid_plural.argtypes = [po_message_t]
    gpo.po_message_prev_msgid_plural.restype = STRING
    gpo.po_message_is_obsolete.argtypes = [po_message_t]
    gpo.po_message_is_obsolete.restype = c_int
    gpo.po_message_is_fuzzy.argtypes = [po_message_t]
    gpo.po_message_is_fuzzy.restype = c_int
    gpo.po_message_is_format.argtypes = [po_message_t, STRING]
    gpo.po_message_is_format.restype = c_int
    gpo.po_message_msgctxt.restype = STRING
    gpo.po_message_msgid.argtypes = [po_message_t]
    gpo.po_message_msgid.restype = STRING
    gpo.po_message_msgid_plural.argtypes = [po_message_t]
    gpo.po_message_msgid_plural.restype = STRING
    gpo.po_message_msgstr.argtypes = [po_message_t]
    gpo.po_message_msgstr.restype = STRING
    gpo.po_message_msgstr_plural.argtypes = [po_message_t, c_int]
    gpo.po_message_msgstr_plural.restype = STRING

    # Message (set methods)
    gpo.po_message_set_comments.argtypes = [po_message_t, STRING]
    gpo.po_message_set_extracted_comments.argtypes = [po_message_t, STRING]
    gpo.po_message_set_prev_msgctxt.argtypes = [po_message_t, STRING]
    gpo.po_message_set_prev_msgid.argtypes = [po_message_t, STRING]
    gpo.po_message_set_prev_msgid_plural.argtypes = [po_message_t, STRING]
    gpo.po_message_set_obsolete.argtypes = [po_message_t, c_int]
    gpo.po_message_set_fuzzy.argtypes = [po_message_t, c_int]
    gpo.po_message_set_format.argtypes = [po_message_t, STRING, c_int]
    gpo.po_message_set_msgctxt.argtypes = [po_message_t, STRING]
    gpo.po_message_set_msgid.argtypes = [po_message_t, STRING]
    gpo.po_message_set_msgstr.argtypes = [po_message_t, STRING]
    gpo.po_message_set_msgstr_plural.argtypes = [po_message_t, c_int, STRING]
    gpo.po_message_set_range.argtypes = [po_message_t, c_int, c_int]


# Load libgettextpo
gpo = None
# 'gettextpo' is recognised on Unix, while only 'libgettextpo' is recognised on
# windows. Therefore we test both.
names = ["gettextpo", "libgettextpo"]
for name in names:
    lib_location = ctypes.util.find_library(name)
    if lib_location:
        gpo = cdll.LoadLibrary(lib_location)
        if gpo:
            break
else:
    # Don't raise exception in Sphinx autodoc [where xml is Mock()ed]. There is
    # nothing special about use of xml here - any of the Mock classes set up
    # in docs/conf.py would work as well, but xml is likely always to be there.
    gpo = None
    if "xml" not in sys.modules or sys.modules["xml"].__path__ != "/dev/null":
        # Now we are getting desperate, so let's guess a unix type DLL that
        # might be in LD_LIBRARY_PATH or loaded with LD_PRELOAD
        try:
            gpo = cdll.LoadLibrary("libgettextpo.so")
        except OSError:
            raise ImportError("gettext PO library not found")

if gpo:
    setup_call_types(gpo)

# Setup the po_xerror_handler
xerror_handler = po_xerror_handler()
xerror_handler.xerror = xerror_prototype(xerror_cb)
xerror_handler.xerror2 = xerror2_prototype(xerror2_cb)


def escapeforpo(text):
    return pypo.escapeforpo(text)


def quoteforpo(text):
    return pypo.quoteforpo(text)


def unquotefrompo(postr):
    return pypo.unquotefrompo(postr)


def get_libgettextpo_version():
    """
    Returns the libgettextpo version.

    :rtype: three-value tuple
    :return: libgettextpo version in the following format::
        (major version, minor version, subminor version)
    """
    libversion = c_long.in_dll(gpo, "libgettextpo_version")
    major = libversion.value >> 16
    minor = (libversion.value >> 8) & 0xFF
    subminor = libversion.value - (major << 16) - (minor << 8)
    return major, minor, subminor


def gpo_encode(value):
    return value.encode("utf-8") if isinstance(value, str) else value


def gpo_decode(value):
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


class pounit(pocommon.pounit):
    #: fixed encoding that is always used for cPO structure (self._gpo_message)
    CPO_ENC = "utf-8"

    def __init__(self, source=None, encoding="utf-8", gpo_message=None):
        self._rich_source = None
        self._rich_target = None
        encoding = encoding or "utf-8"
        if not gpo_message:
            self._gpo_message = gpo.po_message_create()
        if isinstance(source, str):
            self.source = source
            self.target = ""
        elif gpo_message:
            if encoding.lower() != self.CPO_ENC:
                features = ["msgctxt", "msgid", "msgid_plural"]
                features += ["prev_" + x for x in features]
                features += ["comments", "extracted_comments", "msgstr"]
                for feature in features:
                    text = getattr(gpo, "po_message_" + feature)(gpo_message)
                    if text:
                        getattr(gpo, "po_message_set_" + feature)(
                            gpo_message, text.decode(encoding).encode(self.CPO_ENC)
                        )
                # Also iterate through plural forms
                nplural = 0
                text = True
                while text:
                    text = gpo.po_message_msgstr_plural(gpo_message, nplural)
                    if text:
                        gpo.po_message_set_msgstr_plural(
                            gpo_message,
                            text.decode(encoding).encode(self.CPO_ENC),
                            nplural,
                        )
                    nplural += 1
            self._gpo_message = gpo_message
        self.infer_state()

    def infer_state(self):
        # FIXME: do obsolete
        if gpo.po_message_is_obsolete(self._gpo_message):
            if gpo.po_message_is_fuzzy(self._gpo_message):
                self.set_state_n(self.STATE[self.S_FUZZY_OBSOLETE][0])
            else:
                self.set_state_n(self.STATE[self.S_OBSOLETE][0])
        elif gpo.po_message_is_fuzzy(self._gpo_message):
            self.set_state_n(self.STATE[self.S_FUZZY][0])
        elif self.target:
            self.set_state_n(self.STATE[self.S_TRANSLATED][0])
        else:
            self.set_state_n(self.STATE[self.S_UNTRANSLATED][0])

    def setmsgid_plural(self, msgid_plural):
        if isinstance(msgid_plural, list):
            msgid_plural = "".join(msgid_plural)
        gpo.po_message_set_msgid_plural(self._gpo_message, gpo_encode(msgid_plural))

    msgid_plural = property(None, setmsgid_plural)

    @property
    def source(self):
        def remove_msgid_comments(text):
            if not text:
                return text
            if text.startswith("_:"):
                remainder = re.search(r"_: .*\n(.*)", text)
                if remainder:
                    return remainder.group(1)
                return ""
            return text

        singular = remove_msgid_comments(
            gpo_decode(gpo.po_message_msgid(self._gpo_message)) or ""
        )
        if singular:
            if self.hasplural():
                multi = multistring(singular)
                pluralform = (
                    gpo_decode(gpo.po_message_msgid_plural(self._gpo_message)) or ""
                )
                multi.extra_strings.append(pluralform)
                return multi
            return singular
        return ""

    @source.setter
    def source(self, source):
        if isinstance(source, multistring):
            source = source.strings
        if isinstance(source, list):
            gpo.po_message_set_msgid(self._gpo_message, gpo_encode(source[0]))
            if len(source) > 1:
                gpo.po_message_set_msgid_plural(
                    self._gpo_message, gpo_encode(source[1])
                )
        else:
            gpo.po_message_set_msgid(self._gpo_message, gpo_encode(source))
            gpo.po_message_set_msgid_plural(self._gpo_message, None)

    @property
    def target(self):
        if self.hasplural():
            plurals = []
            nplural = 0
            plural = gpo.po_message_msgstr_plural(self._gpo_message, nplural)
            while plural:
                plurals.append(plural.decode(self.CPO_ENC))
                nplural += 1
                plural = gpo.po_message_msgstr_plural(self._gpo_message, nplural)
            multi = multistring(plurals) if plurals else multistring("")
        else:
            multi = gpo_decode(gpo.po_message_msgstr(self._gpo_message)) or ""
        return multi

    @target.setter
    def target(self, target):
        # for plural strings: convert 'target' into a list
        if self.hasplural():
            if isinstance(target, multistring):
                target = target.strings
            elif isinstance(target, str):
                target = [target]
        # for non-plurals: check number of items in 'target'
        elif isinstance(target, (dict, list)):
            if len(target) == 1:
                target = target[0]
            else:
                raise ValueError(
                    "po msgid element has no plural but msgstr has %d elements (%s)"
                    % (len(target), target)
                )
        # empty the previous list of messages
        # TODO: the "pypo" implementation does not remove the previous items of
        #   the target, if self.target == target (essentially: comparing only
        #   the first item of a plural string with the single new string)
        #   Maybe this behaviour should be unified.
        if isinstance(target, (dict, list)):
            i = 0
            message = gpo.po_message_msgstr_plural(self._gpo_message, i)
            while message is not None:
                gpo.po_message_set_msgstr_plural(self._gpo_message, i, None)
                i += 1
                message = gpo.po_message_msgstr_plural(self._gpo_message, i)
        # add the items of a list
        if isinstance(target, list):
            for i, targetstring in enumerate(target):
                gpo.po_message_set_msgstr_plural(
                    self._gpo_message, i, gpo_encode(targetstring)
                )
        # add the values of a dict
        elif isinstance(target, dict):
            for i, targetstring in enumerate(target.values()):
                gpo.po_message_set_msgstr_plural(
                    self._gpo_message, i, gpo_encode(targetstring)
                )
        # add a single string
        elif target is None:
            gpo.po_message_set_msgstr(self._gpo_message, gpo_encode(""))
        else:
            gpo.po_message_set_msgstr(self._gpo_message, gpo_encode(target))

    def getid(self):
        """
        The unique identifier for this unit according to the conventions in
        .mo files.
        """
        id = gpo_decode(gpo.po_message_msgid(self._gpo_message)) or ""
        # Gettext does not consider the plural to determine duplicates, only
        # the msgid. For generation of .mo files, we might want to use this
        # code to generate the entry for the hash table, but for now, it is
        # commented out for conformance to gettext.
        #        plural = gpo.po_message_msgid_plural(self._gpo_message)
        #        if not plural is None:
        #            id = '%s\0%s' % (id, plural)
        context = gpo.po_message_msgctxt(self._gpo_message)
        if context:
            id = f"{gpo_decode(context)}\04{id}"
        return id

    def getnotes(self, origin=None):
        if origin is None:
            comments = gpo.po_message_comments(
                self._gpo_message
            ) + gpo.po_message_extracted_comments(self._gpo_message)
        elif origin == "translator":
            comments = gpo.po_message_comments(self._gpo_message)
        elif origin in {"programmer", "developer", "source code"}:
            comments = gpo.po_message_extracted_comments(self._gpo_message)
        else:
            raise ValueError("Comment type not valid")

        if comments and get_libgettextpo_version() < (0, 17, 0):
            comments = "\n".join(line for line in comments.split("\n"))
        # Let's drop the last newline
        return gpo_decode(comments[:-1])

    def addnote(self, text, origin=None, position="append"):
        # ignore empty strings and strings without non-space characters
        if not (text and text.strip()):
            return
        oldnotes = self.getnotes(origin)
        newnotes = None
        if oldnotes:
            if position == "append":
                newnotes = oldnotes + "\n" + text
            elif position == "merge":
                if oldnotes != text:
                    oldnoteslist = oldnotes.split("\n")
                    for newline in text.split("\n"):
                        newline = newline.rstrip("\r")
                        # avoid duplicate comment lines (this might cause some problems)
                        if newline not in oldnotes or len(newline) < 5:
                            oldnoteslist.append(newline)
                    newnotes = "\n".join(oldnoteslist)
            else:
                newnotes = text + "\n" + oldnotes
        else:
            newnotes = "\n".join(line.rstrip("\r") for line in text.split("\n"))

        if newnotes:
            newlines = []
            needs_space = get_libgettextpo_version() < (0, 17, 0)
            for line in newnotes.split("\n"):
                if line and needs_space:
                    newlines.append(" " + line)
                else:
                    newlines.append(line)
            newnotes = gpo_encode("\n".join(newlines))
            if origin in {"programmer", "developer", "source code"}:
                gpo.po_message_set_extracted_comments(self._gpo_message, newnotes)
            else:
                gpo.po_message_set_comments(self._gpo_message, newnotes)

    def removenotes(self, origin=None):
        gpo.po_message_set_comments(self._gpo_message, b"")

    def copy(self):
        newpo = self.__class__()
        newpo._gpo_message = self._gpo_message
        return newpo

    def merge(self, otherpo, overwrite=False, comments=True, authoritative=False):
        """
        Merges the otherpo (with the same msgid) into this one.

        Overwrite non-blank self.msgstr only if overwrite is True
        merge comments only if comments is True
        """
        if not isinstance(otherpo, pounit):
            super().merge(otherpo, overwrite, comments)
            return
        if comments:
            self.addnote(
                otherpo.getnotes("translator"), origin="translator", position="merge"
            )
            # FIXME mergelists(self.typecomments, otherpo.typecomments)
            if not authoritative:
                # We don't bring across otherpo.automaticcomments as we consider ourself
                # to be the the authority.  Same applies to otherpo.msgidcomments
                self.addnote(
                    otherpo.getnotes("developer"), origin="developer", position="merge"
                )
                self.msgidcomment = otherpo._extract_msgidcomments() or None
                self.addlocations(otherpo.getlocations())
        if not self.istranslated() or overwrite:
            # Remove kde-style comments from the translation (if any).
            if self._extract_msgidcomments(otherpo.target):
                otherpo.target = otherpo.target.replace(
                    "_: " + otherpo._extract_msgidcomments() + "\n", ""
                )
            self.target = otherpo.target
            if (
                self.source != otherpo.source
                or self.getcontext() != otherpo.getcontext()
            ):
                self.markfuzzy()
            else:
                self.markfuzzy(otherpo.isfuzzy())
        elif not otherpo.istranslated():
            if self.source != otherpo.source:
                self.markfuzzy()
        elif self.target != otherpo.target:
            self.markfuzzy()

    def isheader(self):
        # return self.source == "" and self.target != ""
        # we really want to make sure that there is no msgidcomment or msgctxt
        return not self.getid() and len(self.target) > 0

    def isblank(self):
        return len(self.source) == len(self.target) == len(self.getcontext()) == 0

    def hastypecomment(self, typecomment):
        return gpo.po_message_is_format(self._gpo_message, gpo_encode(typecomment))

    def settypecomment(self, typecomment, present=True):
        gpo.po_message_set_format(self._gpo_message, gpo_encode(typecomment), present)

    def hasmarkedcomment(self, commentmarker):
        commentmarker = f"({commentmarker})"
        for comment in self.getnotes("translator").split("\n"):
            if comment.startswith(commentmarker):
                return True
        return False

    def isfuzzy(self):
        return gpo.po_message_is_fuzzy(self._gpo_message)

    def _domarkfuzzy(self, present=True):
        gpo.po_message_set_fuzzy(self._gpo_message, present)

    def makeobsolete(self):
        # FIXME: libgettexpo currently does not reset other data, we probably want to do that
        # but a better solution would be for libgettextpo to output correct data on serialisation
        gpo.po_message_set_obsolete(self._gpo_message, True)
        self.infer_state()

    def resurrect(self):
        gpo.po_message_set_obsolete(self._gpo_message, False)
        self.infer_state()

    def hasplural(self):
        return gpo.po_message_msgid_plural(self._gpo_message) is not None

    def _extract_msgidcomments(self, text=None):
        """
        Extract KDE style msgid comments from the unit.

        :rtype: String
        :return: Returns the extracted msgidcomments found in this unit's msgid.
        """
        if not text:
            text = gpo_decode(gpo.po_message_msgid(self._gpo_message)) or ""
        if text:
            return pocommon.extract_msgid_comment(text)
        return ""

    def setmsgidcomment(self, msgidcomment):
        if msgidcomment:
            self.source = f"_: {msgidcomment}\n{self.source}"

    msgidcomment = property(_extract_msgidcomments, setmsgidcomment)

    def __str__(self):
        pf = pofile(noheader=True)
        pf.addunit(self)
        return bytes(pf).decode(self.CPO_ENC)

    def getlocations(self):
        locations = []
        i = 0
        location = gpo.po_message_filepos(self._gpo_message, i)
        while location:
            locname = gpo_decode(gpo.po_filepos_file(location))
            locline = gpo.po_filepos_start_line(location)
            locstring = locname if locline == -1 else ":".join([locname, str(locline)])
            locations.append(pocommon.unquote_plus(locstring))
            i += 1
            location = gpo.po_message_filepos(self._gpo_message, i)
        return locations

    def addlocation(self, location):
        if location.find(" ") != -1:
            location = pocommon.quote_plus(location)
        parts = location.split(":")
        if len(parts) == 2 and parts[1].isdigit():
            file = parts[0]
            line = int(parts[1] or "0")
        else:
            file = location
            line = -1
        gpo.po_message_add_filepos(self._gpo_message, gpo_encode(file), line)

    def getcontext(self):
        msgctxt = gpo.po_message_msgctxt(self._gpo_message)
        if msgctxt:
            return gpo_decode(msgctxt)
        return self._extract_msgidcomments()

    def setcontext(self, context):
        gpo.po_message_set_msgctxt(self._gpo_message, gpo_encode(context))

    @classmethod
    def buildfromunit(cls, unit, encoding=None):
        """
        Build a native unit from a foreign unit, preserving as much
        information as possible.
        """
        if type(unit) is cls and hasattr(unit, "copy") and callable(unit.copy):
            return unit.copy()
        if isinstance(unit, pocommon.pounit):
            newunit = cls(unit.source, encoding)
            newunit.target = unit.target
            # context
            newunit.msgidcomment = unit._extract_msgidcomments()
            context = unit.getcontext()
            if not newunit.msgidcomment and context:
                newunit.setcontext(context)

            locations = unit.getlocations()
            if locations:
                newunit.addlocations(locations)
            notes = unit.getnotes("developer")
            if notes:
                newunit.addnote(notes, "developer")
            notes = unit.getnotes("translator")
            if notes:
                newunit.addnote(notes, "translator")
            if unit.isobsolete():
                newunit.makeobsolete()
            newunit.markfuzzy(unit.isfuzzy())
            for tc in ["python-format", "c-format", "php-format"]:
                if unit.hastypecomment(tc):
                    newunit.settypecomment(tc)
                    # We assume/guess/hope that there will only be one
                    break
            return newunit
        return base.TranslationUnit.buildfromunit(unit)


class pofile(pocommon.pofile):
    UnitClass = pounit

    def __init__(self, inputfile=None, noheader=False, **kwargs):
        self._gpo_memory_file = None
        self._gpo_message_iterator = None
        self.sourcelanguage = None
        self.targetlanguage = None
        if inputfile is None:
            self.units = []
            self._encoding = kwargs.get("encoding")
            self._gpo_memory_file = gpo.po_file_create()
            self._gpo_message_iterator = gpo.po_message_iterator(
                self._gpo_memory_file, None
            )
        super().__init__(inputfile=inputfile, noheader=noheader, **kwargs)

    def addunit(self, unit, new=True):
        if new:
            gpo.po_message_insert(self._gpo_message_iterator, unit._gpo_message)
        super().addunit(unit)

    def removeunit(self, unit):
        # There seems to be no API to remove a message
        raise ValueError("Unit removal not supported by cpo")

    def _insert_header(self, header):
        header._store = self
        self.units.insert(0, header)
        self._free_iterator()
        self._gpo_message_iterator = gpo.po_message_iterator(
            self._gpo_memory_file, None
        )
        gpo.po_message_insert(self._gpo_message_iterator, header._gpo_message)
        while gpo.po_next_message(self._gpo_message_iterator):
            pass

    def removeduplicates(self, duplicatestyle="merge"):
        """Make sure each msgid is unique ; merge comments etc from duplicates into original."""
        # TODO: can we handle consecutive calls to removeduplicates()? What
        # about files already containing msgctxt? - test
        id_dict = {}
        uniqueunits = []
        # TODO: this is using a list as the pos aren't hashable, but this is slow.
        # probably not used frequently enough to worry about it, though.
        markedpos = []

        def addcomment(thepo):
            thepo.msgidcomment = " ".join(thepo.getlocations())
            markedpos.append(thepo)

        for thepo in self.units:
            id = thepo.getid()
            if thepo.isheader() and not thepo.getlocations():
                # header msgids shouldn't be merged...
                uniqueunits.append(thepo)
            elif id in id_dict:
                if duplicatestyle == "merge":
                    if id:
                        id_dict[id].merge(thepo)
                    else:
                        addcomment(thepo)
                        uniqueunits.append(thepo)
                elif duplicatestyle == "msgctxt":
                    origpo = id_dict[id]
                    if origpo not in markedpos:
                        origpo.setcontext(" ".join(origpo.getlocations()))
                        markedpos.append(thepo)
                    thepo.setcontext(" ".join(thepo.getlocations()))
                    thepo_msgctxt = gpo.po_message_msgctxt(thepo._gpo_message)
                    idpo_msgctxt = gpo.po_message_msgctxt(id_dict[id]._gpo_message)
                    if thepo_msgctxt != idpo_msgctxt:
                        uniqueunits.append(thepo)
                    else:
                        logger.warning(
                            "Duplicate unit found with msgctx of '%s' and source '%s'",
                            thepo_msgctxt,
                            thepo.source,
                        )
            else:
                if not id:
                    if duplicatestyle == "merge":
                        addcomment(thepo)
                    else:
                        thepo.setcontext(" ".join(thepo.getlocations()))
                id_dict[id] = thepo
                uniqueunits.append(thepo)
        new_gpo_memory_file = gpo.po_file_create()
        new_gpo_message_iterator = gpo.po_message_iterator(new_gpo_memory_file, None)
        for unit in uniqueunits:
            gpo.po_message_insert(new_gpo_message_iterator, unit._gpo_message)
        self._free_iterator()
        self._gpo_message_iterator = new_gpo_message_iterator
        self._free_memory_file()
        self._gpo_memory_file = new_gpo_memory_file
        self.units = uniqueunits

    def serialize(self, out):
        def obsolete_workaround():
            # Remove all items that are not output by msgmerge when a unit is obsolete.  This is a work
            # around for bug in libgettextpo
            # FIXME Do version test in case they fix this bug
            for unit in self.units:
                if unit.isobsolete():
                    gpo.po_message_set_extracted_comments(unit._gpo_message, b"")
                    location = gpo.po_message_filepos(unit._gpo_message, 0)
                    while location:
                        gpo.po_message_remove_filepos(unit._gpo_message, 0)
                        location = gpo.po_message_filepos(unit._gpo_message, 0)

        def writefile(filename):
            xerror_storage.exception = None
            result = gpo.po_file_write_v2(
                self._gpo_memory_file, gpo_encode(filename), xerror_handler
            )
            if xerror_storage.exception is not None:
                raise xerror_storage.exception
            if result is None:
                raise ValueError("Unknown error while saving file")
            with open(filename, "rb") as tfile:
                return tfile.read()

        outputstring = ""
        if self._gpo_memory_file:
            obsolete_workaround()
            f, fname = tempfile.mkstemp(prefix="translate", suffix=".po")
            os.close(f)
            try:
                outputstring = writefile(fname)
                if self.encoding != pounit.CPO_ENC:
                    try:
                        outputstring = outputstring.decode(pounit.CPO_ENC).encode(
                            self.encoding
                        )
                    except UnicodeEncodeError:
                        self.encoding = pounit.CPO_ENC
                        self.updateheader(
                            content_type="text/plain; charset=UTF-8",
                            content_transfer_encoding="8bit",
                        )
                        outputstring = writefile(fname)
            finally:
                os.remove(fname)
        out.write(outputstring)

    def isempty(self):
        """Returns True if the object doesn't contain any translation units."""
        if len(self.units) == 0:
            return True
        # Skip the first unit if it is a header.
        units = self.units[1:] if self.units[0].isheader() else self.units

        return all(not (not unit.isblank() and not unit.isobsolete()) for unit in units)

    def parse(self, input):
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""

        if hasattr(input, "read"):
            posrc = input.read()
            input.close()
            input = posrc

        needtmpfile = not os.path.isfile(input)
        if needtmpfile:
            # This is not a file - we write the string to a temporary file
            fd, fname = tempfile.mkstemp(prefix="translate", suffix=".po")
            os.write(fd, input)
            input = fname
            os.close(fd)

        try:
            xerror_storage.exception = None
            self._free_memory_file()
            self._gpo_memory_file = gpo.po_file_read_v3(
                gpo_encode(input), xerror_handler
            )
            if xerror_storage.exception is not None:
                raise xerror_storage.exception
            if self._gpo_memory_file is None:
                logger.error("Error:")
        finally:
            if needtmpfile:
                os.remove(input)

        self.units = []
        # Handle xerrors here
        self._header = gpo.po_file_domain_header(self._gpo_memory_file, None)
        if self._header:
            charset = gpo_decode(
                gpo.po_header_field(self._header, gpo_encode("Content-Type"))
            )
            if charset:
                charset = re.search("charset=([^\\s]+)", charset).group(1)
            self.encoding = charset
        self._free_iterator()
        self._gpo_message_iterator = gpo.po_message_iterator(
            self._gpo_memory_file, None
        )
        newmessage = gpo.po_next_message(self._gpo_message_iterator)
        while newmessage:
            newunit = pounit(gpo_message=newmessage, encoding=self.encoding)
            self.addunit(newunit, new=False)
            newmessage = gpo.po_next_message(self._gpo_message_iterator)
        self._free_iterator()

    def __del__(self):
        self._free_iterator()
        self._free_memory_file()

    def _free_memory_file(self):
        return
        if self._gpo_memory_file is not None:
            gpo.po_file_free(self._gpo_memory_file)
            self._gpo_memory_file = None

    def _free_iterator(self):
        if self._gpo_message_iterator is not None:
            gpo.po_message_iterator_free(self._gpo_message_iterator)
            self._gpo_message_iterator = None
