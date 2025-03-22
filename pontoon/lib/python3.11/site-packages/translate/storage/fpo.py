#
# Copyright 2002-2011 Zuza Software Foundation
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
Classes for the support of Gettext .po and .pot files.

This implementation assumes that cpo is working. This should not be used
directly, but can be used once cpo has been established to work.
"""

# TODO:
# - handle headerless PO files better
# - previous msgid and msgctxt
# - accept only unicodes everywhere

import copy
import logging
import re

from translate.misc.multistring import multistring
from translate.storage import base, cpo, pocommon

logger = logging.getLogger(__name__)


lsep = " "
"""Separator for #: entries"""

basic_header = r"""msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"""


class pounit(pocommon.pounit):
    # othercomments = []      #   # this is another comment
    # automaticcomments = []  #   #. comment extracted from the source code
    # sourcecomments = []     #   #: sourcefile.xxx:35
    # prev_msgctxt = []       #   #| The previous values that msgctxt and msgid held
    # prev_msgid = []         #
    # prev_msgid_plural = []  #
    # typecomments = []       #   #, fuzzy
    # msgidcomment = ""      #   _: within msgid
    # msgctxt
    # msgid = []
    # msgstr = []

    # Our homegrown way to indicate what must be copied in a shallow
    # fashion
    __shallow__ = ["_store"]

    def __init__(self, source=None, **kwargs):
        super().__init__(source)
        self._initallcomments(blankall=True)
        self._msgctxt = ""

        self.target = ""

    def _initallcomments(self, blankall=False):
        """Initialises allcomments."""
        if blankall:
            self.othercomments = []
            self.automaticcomments = []
            self.sourcecomments = []
            self.typecomments = []
            self.msgidcomment = ""

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._rich_source = None
        source = source or ""
        if isinstance(source, (multistring, str)):
            self._source = source
        else:  # If it is unicode, list or dict.
            self._source = multistring(source)

    @property
    def target(self):
        """Returns the unescaped msgstr."""
        return self._target

    @target.setter
    def target(self, target):
        """Sets the msgstr to the given (unescaped) value."""
        self._rich_target = None
        if self.hasplural():
            if isinstance(target, multistring):
                self._target = target
            else:  # If it is unicode, list or dict.
                self._target = multistring(target)
        elif isinstance(target, (dict, list)):
            if len(target) == 1:
                self._target = target[0]
            else:
                raise ValueError(
                    "po msgid element has no plural but msgstr"
                    "has %d elements (%s)" % (len(target), target)
                )
        else:
            self._target = target

    def getnotes(self, origin=None):
        """Return comments based on origin value (programmer, developer, source code and translator)."""
        if origin is None:
            comments = "\n".join(self.othercomments)
            comments += "\n".join(self.automaticcomments)
        elif origin == "translator":
            comments = "\n".join(self.othercomments)
        elif origin in {"programmer", "developer", "source code"}:
            comments = "\n".join(self.automaticcomments)
        else:
            raise ValueError("Comment type not valid")
        return comments

    def addnote(self, text, origin=None, position="append"):
        """This is modeled on the XLIFF method. See xliff.py::xliffunit.addnote."""
        # ignore empty strings and strings without non-space characters
        if not (text and text.strip()):
            return
        commentlist = self.othercomments
        autocomments = False
        if origin in {"programmer", "developer", "source code"}:
            autocomments = True
            commentlist = self.automaticcomments
        text = text.removesuffix("\n")
        newcomments = text.split("\n")
        if position == "append":
            newcomments = commentlist + newcomments
        elif position == "prepend":
            newcomments += commentlist

        if autocomments:
            self.automaticcomments = newcomments
        else:
            self.othercomments = newcomments

    def removenotes(self, origin=None):
        """Remove all the translator's notes (other comments)."""
        self.othercomments = []

    def __deepcopy__(self, memo={}):
        # Make an instance to serve as the copy
        new_unit = self.__class__()
        # We'll be testing membership frequently, so make a set from
        # self.__shallow__
        shallow = set(self.__shallow__)
        # Make deep copies of all members which are not in shallow
        for key, value in self.__dict__.items():
            if key not in shallow:
                setattr(new_unit, key, copy.deepcopy(value))
        # Make shallow copies of all members which are in shallow
        for key in set(shallow):
            setattr(new_unit, key, getattr(self, key))
        # Mark memo with ourself, so that we won't get deep copied
        # again
        memo[id(self)] = self
        # Return our copied unit
        return new_unit

    def copy(self):
        return copy.deepcopy(self)

    def _msgidlen(self):
        if self.hasplural():
            return len("".join(string for string in self.source.strings))
        return len(self.source)

    def _msgstrlen(self):
        if self.hasplural():
            return len("".join(string for string in self.target.strings))
        return len(self.target)

    def merge(self, otherpo, overwrite=False, comments=True, authoritative=False):
        """
        Merges the otherpo (with the same msgid) into this one.

        Overwrite non-blank self.msgstr only if overwrite is True
        merge comments only if comments is True
        """

        def mergelists(list1, list2, split=False):
            # Determine the newline style of list2
            lineend = ""
            if list2 and list2[0]:
                for candidate in ["\n", "\r", "\n\r"]:
                    if list2[0].endswith(candidate):
                        lineend = candidate
                if not lineend:
                    lineend = ""

            # Split if directed to do so:
            if split:
                splitlist1 = []
                splitlist2 = []
                for item in list1:
                    splitlist1.extend(item.split())
                for item in list2:
                    splitlist2.extend(item.split())
                list1.extend([item for item in splitlist2 if item not in splitlist1])
            elif list1 != list2:
                # Normal merge, but conform to list1 newline style
                for item in list2:
                    item = item.rstrip(lineend)
                    # avoid duplicate comment lines (this might cause some problems)
                    if item not in list1 or len(item) < 5:
                        list1.append(item)

        if not isinstance(otherpo, pounit):
            super().merge(otherpo, overwrite, comments)
            return
        if comments:
            mergelists(self.othercomments, otherpo.othercomments)
            mergelists(self.typecomments, otherpo.typecomments)
            if not authoritative:
                # We don't bring across otherpo.automaticcomments as we consider ourself
                # to be the the authority.  Same applies to otherpo.msgidcomments
                mergelists(self.automaticcomments, otherpo.automaticcomments)
                #                mergelists(self.msgidcomments, otherpo.msgidcomments) #XXX?
                mergelists(self.sourcecomments, otherpo.sourcecomments, split=True)
        if not self.istranslated() or overwrite:
            # Remove kde-style comments from the translation (if any). XXX - remove
            if pocommon.extract_msgid_comment(otherpo.target):
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
        # TODO: fix up nicely
        return not self.getid() and len(self.target) > 0

    def isblank(self):
        return (
            not self.isheader()
            and not self.msgidcomment
            and (self._msgidlen() == 0)
            and (self._msgstrlen() == 0)
            and len(self._msgctxt) == 0
        )

    def hastypecomment(self, typecomment):
        """Check whether the given type comment is present."""
        # check for word boundaries properly by using a regular expression...
        return (
            sum(
                len(re.findall(f"\\b{typecomment}\\b", tcline))
                for tcline in self.typecomments
            )
            != 0
        )

    def hasmarkedcomment(self, commentmarker):
        """Check whether the given comment marker is present as # (commentmarker) ..."""
        commentmarker = f"({commentmarker})"
        return any(comment.startswith(commentmarker) for comment in self.othercomments)

    def settypecomment(self, typecomment, present=True):
        """Alters whether a given typecomment is present."""
        if self.hastypecomment(typecomment) != present:
            if present:
                self.typecomments.append(f"#, {typecomment}\n")
            else:
                # this should handle word boundaries properly ...
                typecomments = [
                    re.sub(f"\\b{typecomment}\\b[ \t,]*", "", tcline)
                    for tcline in self.typecomments
                ]
                self.typecomments = filter(
                    lambda tcline: tcline.strip() != "#,", typecomments
                )

    def istranslated(self):
        return super().istranslated() and not self.isobsolete()

    def istranslatable(self):
        return not (self.isheader() or self.isblank() or self.isobsolete())

    def isfuzzy(self):
        return self.hastypecomment("fuzzy")

    def _domarkfuzzy(self, present=True):
        self.settypecomment("fuzzy", present)

    def makeobsolete(self):
        """Makes this unit obsolete."""
        self.sourcecomments = []
        self.automaticcomments = []
        super().makeobsolete()

    def hasplural(self):
        """Returns whether this pounit contains plural strings..."""
        source = self.source
        return isinstance(source, multistring) and len(source.strings) > 1

    def __str__(self):
        """Convert to a string. double check that unicode is handled somehow here."""
        _cpo_unit = cpo.pounit.buildfromunit(self)
        return str(_cpo_unit)

    def getlocations(self):
        """
        Get a list of locations from sourcecomments in the PO unit.

        rtype: List
        return: A list of the locations with '#: ' stripped

        """
        # TODO: rename to .locations
        return self.sourcecomments

    def addlocation(self, location):
        """
        Add a location to sourcecomments in the PO unit.

        :param location: Text location e.g. 'file.c:23' does not include #:
        :type location: String
        """
        self.sourcecomments.append(location)

    def _extract_msgidcomments(self, text=None):
        """
        Extract KDE style msgid comments from the unit.

        :rtype: String
        :return: Returns the extracted msgidcomments found in this unit's msgid.
        """
        if text:
            return pocommon.extract_msgid_comment(text)
        return self.msgidcomment

    def getcontext(self):
        """Get the message context."""
        return self._msgctxt + self.msgidcomment

    def setcontext(self, context):
        self._msgctxt = context or ""

    def getid(self):
        """Returns a unique identifier for this unit."""
        context = self.getcontext()
        # Gettext does not consider the plural to determine duplicates, only
        # the msgid. For generation of .mo files, we might want to use this
        # code to generate the entry for the hash table, but for now, it is
        # commented out for conformance to gettext.
        #        id = '\0'.join(self.source.strings)
        id = self.source
        if self.msgidcomment:
            id = f"_: {context}\n{id}"
        elif context:
            id = f"{context}\04{id}"
        return id

    @classmethod
    def buildfromunit(cls, unit):
        """
        Build a native unit from a foreign unit, preserving as much
        information as possible.
        """
        if type(unit) is cls and hasattr(unit, "copy") and callable(unit.copy):
            return unit.copy()
        if isinstance(unit, pocommon.pounit):
            newunit = cls(unit.source)
            newunit.target = unit.target
            # context
            newunit.msgidcomment = unit._extract_msgidcomments()
            if not newunit.msgidcomment:
                newunit.setcontext(unit.getcontext())

            locations = unit.getlocations()
            if locations:
                newunit.addlocations(locations)
            notes = unit.getnotes("developer")
            if notes:
                newunit.addnote(notes, "developer")
            notes = unit.getnotes("translator")
            if notes:
                newunit.addnote(notes, "translator")
            newunit.markfuzzy(unit.isfuzzy())
            if unit.isobsolete():
                newunit.makeobsolete()
            for tc in ["python-format", "c-format", "php-format"]:
                if unit.hastypecomment(tc):
                    newunit.settypecomment(tc)
                    break
            return newunit
        return base.TranslationUnit.buildfromunit(unit)


class pofile(pocommon.pofile):
    """A .po file containing various units."""

    UnitClass = pounit

    def _build_self_from_cpo(self):
        """
        Builds up this store from the internal cpo store.

        A user must ensure that self._cpo_store already exists, and that it is
        deleted afterwards.
        """
        for unit in self._cpo_store.units:
            self.addunit(self.UnitClass.buildfromunit(unit))
        self.encoding = self._cpo_store.encoding

    def _build_cpo_from_self(self):
        """
        Builds the internal cpo store from the data in self.

        A user must ensure that self._cpo_store does not exist, and should
        delete it after using it.
        """
        self._cpo_store = cpo.pofile(noheader=True)
        for unit in self.units:
            if not unit.isblank():
                self._cpo_store.addunit(
                    cpo.pofile.UnitClass.buildfromunit(unit, self.encoding)
                )
        if not self._cpo_store.header():
            # only add a temporary header
            self._cpo_store.makeheader(charset=self.encoding, encoding="8bit")

    def parse(self, input):
        """Parses the given file or file source string."""
        try:
            if hasattr(input, "name"):
                self.filename = input.name
            elif not getattr(self, "filename", ""):
                self.filename = ""
            self.units = []
            self._cpo_store = cpo.pofile(input, noheader=True)
            self._build_self_from_cpo()
            del self._cpo_store
        except Exception as e:
            raise base.ParseError(e)

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
                    if origpo not in markedpos and id:
                        # if it doesn't have an id, we already added msgctxt
                        origpo._msgctxt += " ".join(origpo.getlocations())
                        markedpos.append(thepo)
                    thepo._msgctxt += " ".join(thepo.getlocations())
                    if thepo._msgctxt != id_dict[id]._msgctxt:
                        uniqueunits.append(thepo)
                    else:
                        logger.warning(
                            "Duplicate unit found with msgctx of '%s' and source '%s'",
                            thepo._msgctxt,
                            thepo.source,
                        )
            else:
                if not id:
                    if duplicatestyle == "merge":
                        addcomment(thepo)
                    else:
                        thepo._msgctxt += " ".join(thepo.getlocations())
                id_dict[id] = thepo
                uniqueunits.append(thepo)
        self.units = uniqueunits

    def serialize(self, out):
        """Write content to file."""
        self._cpo_store = cpo.pofile(encoding=self.encoding, noheader=True)
        try:
            self._build_cpo_from_self()
        except UnicodeEncodeError:
            self.encoding = "utf-8"
            self.updateheader(add=True, Content_Type="text/plain; charset=UTF-8")
            self._build_cpo_from_self()
        self._cpo_store.serialize(out)
        del self._cpo_store
