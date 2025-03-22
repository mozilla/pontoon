#
# Copyright 2002-2008 Zuza Software Foundation
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
Classes that hold units of .oo files (oounit) or entire files (oofile).

These are specific .oo files for localisation exported by OpenOffice.org - SDF
format (previously knows as GSI files).

.. There used to be an overview of the format here
   http://l10n.openoffice.org/L10N_Framework/Intermediate_file_format.html

The behaviour in terms of escaping is explained in detail in the programming
comments.
"""
# FIXME: add simple test which reads in a file and writes it out again

import os
import re
import warnings
from io import BytesIO

from translate.misc import quote, wStringIO

# File normalisation

normalfilenamechars = (
    b"/#.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
)


class normalizechar(dict):
    def __init__(self, normalchars):
        self.normalchars = {}
        for char in normalchars:
            self.normalchars[ord(char)] = char

    def __getitem__(self, key):
        return self.normalchars.get(key, "_")


normalizetable = normalizechar(normalfilenamechars.decode("ascii"))


def normalizefilename(filename):
    """Converts any non-alphanumeric (standard roman) characters to _."""
    return filename.translate(normalizetable)


def makekey(ookey, long_keys):
    """
    converts an oo key tuple into a unique identifier.

    :param ookey: an oo key
    :type ookey: tuple
    :param long_keys: Use long keys
    :type long_keys: Boolean
    :rtype: str
    :return: unique ascii identifier
    """
    project, sourcefile, resourcetype, groupid, localid, platform = ookey
    sourcefile = sourcefile.replace("\\", "/")
    if long_keys:
        sourcebase = f"{project}/{sourcefile}"
    else:
        sourceparts = sourcefile.split("/")
        sourcebase = "".join(sourceparts[-1:])
    if len(groupid) == 0 or len(localid) == 0:
        fullid = groupid + localid
    else:
        fullid = groupid + "." + localid
    if resourcetype:
        fullid = fullid + "." + resourcetype
    key = f"{sourcebase}#{fullid}"
    return normalizefilename(key)


# These are functions that deal with escaping and unescaping of the text fields
# of the SDF file. These should only be applied to the text column.
# The fields quickhelptext and title are assumed to carry no escaping.
#
# The escaping of all strings except those coming from .xhp (helpcontent2)
# sourcefiles work as follows:
#   (newline)         ->  \n
#   (carriage return) ->  \r
#   (tab)             ->  \t
# Backslash characters (\) and single quotes (') are not consistently escaped,
# and are therefore left as they are.
#
# For strings coming from .xhp (helpcontent2) sourcefiles the following
# characters are escaped inside XML tags only:
#   <  ->  \<  when used with lowercase tagnames (with some exceptions)
#   >  ->  \>  when used with lowercase tagnames (with some exceptions)
#   "  ->  \"  around XML properties
# The following is consistently escaped in .xhp strings (not only in XML tags):
#   \  ->  \\


def escape_text(text):
    """Escapes SDF text to be suitable for unit consumption."""
    return text.replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")


def unescape_text(text):
    """Unescapes SDF text to be suitable for unit consumption."""
    return (
        text.replace("\\\\", "\a")
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\r", "\r")
        .replace("\a", "\\\\")
    )


helptagre = re.compile(r"""<[/]??[a-z_\-]+?(?:| +[a-z]+?=".*?") *[/]??>""")


def escape_help_text(text):
    """
    Escapes the help text as it would be in an SDF file.

    <, >, " are only escaped in <[[:lower:]]> tags. Some HTML tags make it in in
    lowercase so those are dealt with. Some OpenOffice.org help tags are not
    escaped.
    """
    text = text.replace("\\", "\\\\")
    for tag in helptagre.findall(text):
        escapethistag = False
        for escape_tag in [
            "ahelp",
            "link",
            "item",
            "emph",
            "defaultinline",
            "switchinline",
            "caseinline",
            "variable",
            "bookmark_value",
            "image",
            "embedvar",
            "alt",
        ]:
            if tag.startswith(f"<{escape_tag}") or tag == f"</{escape_tag}>":
                escapethistag = True
        if tag in {"<br/>", "<help-id-missing/>"}:
            escapethistag = True
        if escapethistag:
            escaped_tag = ("\\<" + tag[1:-1] + "\\>").replace('"', '\\"')
            text = text.replace(tag, escaped_tag)
    return text


def unescape_help_text(text):
    """Unescapes normal text to be suitable for writing to the SDF file."""
    return (
        text.replace(r"\<", "<")
        .replace(r"\>", ">")
        .replace(r"\"", '"')
        .replace(r"\\", "\\")
    )


class ooline:
    """this represents one line, one translation in an .oo file."""

    def __init__(self, parts=None):
        """Construct an ooline from its parts."""
        if parts is None:
            (
                self.project,
                self.sourcefile,
                self.dummy,
                self.resourcetype,
                self.groupid,
                self.localid,
                self.helpid,
                self.platform,
                self.width,
                self.languageid,
                self.text,
                self.helptext,
                self.quickhelptext,
                self.title,
                self.timestamp,
            ) = [""] * 15
        else:
            self.setparts(parts)

    def setparts(self, parts):
        """Create a line from its tab-delimited parts."""
        if len(parts) != 15:
            warnings.warn(
                "oo line contains %d parts, it should contain 15: %r"
                % (len(parts), parts)
            )
            newparts = list(parts)
            if len(newparts) < 15:
                newparts += [""] * (15 - len(newparts))
            else:
                newparts = newparts[:15]
            parts = tuple(newparts)
        (
            self.project,
            self.sourcefile,
            self.dummy,
            self.resourcetype,
            self.groupid,
            self.localid,
            self.helpid,
            self.platform,
            self.width,
            self.languageid,
            self._text,
            self.helptext,
            self.quickhelptext,
            self.title,
            self.timestamp,
        ) = parts

    def getparts(self):
        """Return a list of parts in this line."""
        return (
            self.project,
            self.sourcefile,
            self.dummy,
            self.resourcetype,
            self.groupid,
            self.localid,
            self.helpid,
            self.platform,
            self.width,
            self.languageid,
            self._text,
            self.helptext,
            self.quickhelptext,
            self.title,
            self.timestamp,
        )

    def gettext(self):
        """Obtains the text column and handle escaping."""
        if self.sourcefile.endswith(".xhp"):
            return unescape_help_text(self._text)
        return unescape_text(self._text)

    def settext(self, text):
        """Sets the text column and handle escaping."""
        if self.sourcefile.endswith(".xhp"):
            self._text = escape_help_text(text)
        else:
            self._text = escape_text(text)

    text = property(gettext, settext)

    def __str__(self):
        """Convert to a string."""
        return self.getoutput()

    def getoutput(self):
        """Return a line in tab-delimited form."""
        parts = self.getparts()
        return "\t".join(parts)

    def getkey(self):
        """Get the key that identifies the resource."""
        return (
            self.project,
            self.sourcefile,
            self.resourcetype,
            self.groupid,
            self.localid,
            self.platform,
        )


class oounit:
    """this represents a number of translations of a resource."""

    def __init__(self):
        """Construct the oounit."""
        self.languages = {}
        self.lines = []

    def addline(self, line):
        """Add a line to the oounit."""
        self.languages[line.languageid] = line
        self.lines.append(line)

    def __str__(self):
        """Convert to a string."""
        return self.getoutput()

    def getoutput(self, skip_source=False, fallback_lang=None):
        """Return the lines in tab-delimited form."""
        if skip_source:
            lines = self.lines[1:]
            if not lines:
                # Untranslated, so let's do fall-back: (bug 1883)
                new_line = ooline(self.lines[0].getparts())
                new_line.languageid = fallback_lang
                lines = [new_line]
        else:
            lines = self.lines
        return "\r\n".join(str(line) for line in lines)


class oofile:
    """this represents an entire .oo file."""

    UnitClass = oounit
    encoding = "utf-8"

    def __init__(self, input=None):
        """Constructs the oofile."""
        self.oolines = []
        self.units = []
        self.ookeys = {}
        self.filename = ""
        self.languages = []
        if input is not None:
            self.parse(input)

    def addline(self, thisline):
        """Adds a parsed line to the file."""
        key = thisline.getkey()
        element = self.ookeys.get(key)
        if element is None:
            element = self.UnitClass()
            self.units.append(element)
            self.ookeys[key] = element
        element.addline(thisline)
        self.oolines.append(thisline)
        if thisline.languageid not in self.languages:
            self.languages.append(thisline.languageid)

    def parse(self, input):
        """Parses lines and adds them to the file."""
        if not self.filename:
            self.filename = getattr(input, "name", "")
        if hasattr(input, "read"):
            src = input.read()
            input.close()
        else:
            src = input
        src = src.decode(self.encoding)
        for line in src.split("\n"):
            line = quote.rstripeol(line)
            if not line:
                continue
            parts = line.split("\t")
            thisline = ooline(parts)
            self.addline(thisline)

    def __bytes__(self):
        out = BytesIO()
        self.serialize(out)
        return out.getvalue()

    def serialize(self, out, skip_source=False, fallback_lang=None):
        """Convert to a string. double check that unicode is handled."""
        out.write(self.getoutput(skip_source, fallback_lang).encode(self.encoding))

    def getoutput(self, skip_source=False, fallback_lang=None):
        """Converts all the lines back to tab-delimited form."""
        lines = []
        for oe in self.units:
            if len(oe.lines) > 2:
                warnings.warn(
                    "contains %d lines (should be 2 at most): languages %r"
                    % (len(oe.lines), oe.languages)
                )
                oekeys = [line.getkey() for line in oe.lines]
                warnings.warn(
                    "contains %d lines (should be 2 at most): keys %r"
                    % (len(oe.lines), oekeys)
                )
            oeline = oe.getoutput(skip_source, fallback_lang) + "\r\n"
            lines.append(oeline)
        return "".join(lines)


class oomultifile:
    """
    this takes a huge GSI file and represents it as multiple smaller
    files...
    """

    encoding = "utf-8"

    def __init__(self, filename, mode=None, multifilestyle="single"):
        """Initialises oomultifile from a seekable inputfile or writable outputfile."""
        self.filename = filename
        if mode is None:
            mode = "r" if os.path.exists(filename) else "w"
        self.mode = mode
        self.multifilestyle = multifilestyle
        self.multifilename = os.path.splitext(filename)[0]
        self.multifile = open(filename, mode)
        self.subfilelines = {}
        if mode.startswith("r"):
            self.createsubfileindex()

    def createsubfileindex(self):
        """Reads in all the lines and works out the subfiles."""
        for linenum, line in enumerate(self.multifile):
            subfile = self.getsubfilename(line)
            if subfile not in self.subfilelines:
                self.subfilelines[subfile] = []
            self.subfilelines[subfile].append(linenum)

    def getsubfilename(self, line):
        """Looks up the subfile name for the line."""
        if line.count("\t") < 2:
            raise ValueError(f"invalid tab-delimited line: {line!r}")
        lineparts = line.split("\t", 2)
        module, filename = lineparts[0], lineparts[1]
        if self.multifilestyle == "onefile":
            ooname = self.multifilename
        elif self.multifilestyle == "toplevel":
            ooname = module
        else:
            filename = filename.replace("\\", "/")
            fileparts = [module, *filename.split("/")]
            ooname = os.path.join(*fileparts[:-1])
        return ooname + os.extsep + "oo"

    def listsubfiles(self):
        """Returns a list of subfiles in the file."""
        return self.subfilelines.keys()

    def __iter__(self):
        """Iterates through the subfile names."""
        yield from self.listsubfiles()

    def __contains__(self, pathname):
        """Checks if this pathname is a valid subfile."""
        return pathname in self.subfilelines

    def getsubfilesrc(self, subfile):
        """Returns the list of lines matching the subfile."""
        lines = []
        requiredlines = dict.fromkeys(self.subfilelines[subfile])
        self.multifile.seek(0)
        for linenum, line in enumerate(self.multifile):
            if linenum in requiredlines:
                lines.append(line)
        return "".join(lines)

    def openinputfile(self, subfile):
        """Returns a pseudo-file object for the given subfile."""
        subfilesrc = self.getsubfilesrc(subfile)
        inputfile = BytesIO(subfilesrc.encode())
        inputfile.filename = subfile
        return inputfile

    def openoutputfile(self, subfile):
        """Returns a pseudo-file object for the given subfile."""

        def onclose(contents):
            if isinstance(contents, bytes):
                contents = contents.decode(self.encoding)
            self.multifile.write(contents)
            self.multifile.flush()

        outputfile = wStringIO.CatchStringOutput(onclose)
        outputfile.filename = subfile
        return outputfile

    def getoofile(self, subfile):
        """Returns an oofile built up from the given subfile's lines."""
        subfilesrc = self.getsubfilesrc(subfile)
        oosubfile = oofile()
        oosubfile.filename = subfile
        oosubfile.parse(subfilesrc)
        return oosubfile
