#
# Copyright 2004-2014 Zuza Software Foundation
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

r"""
Classes that hold units of .properties, and similar, files that are used in
translating Java, Mozilla, MacOS and other software.

The :class:`propfile` class is a monolingual class with :class:`propunit`
providing unit level access.

The .properties store has become a general key value pair class with
:class:`Dialect` providing the ability to change the behaviour of the
parsing and handling of the various dialects.

Currently we support:

- Java .properties
- Mozilla .properties
- Adobe Flex files
- MacOS X .strings files
- Skype .lang files
- XWiki .properties

The following provides references and descriptions of the various
dialects supported:

Java
    Java .properties are supported completely except for the ability to drop
    pairs that are not translated.

    The following `.properties file description
    <http://docs.oracle.com/javase/7/docs/api/java/util/Properties.html#load(java.io.Reader)>`_
    gives a good references to the .properties specification.

    Properties file may also hold Java `MessageFormat
    <http://docs.oracle.com/javase/7/docs/api/java/text/MessageFormat.html>`_
    messages.  No special handling is provided in this storage class for
    MessageFormat, but this may be implemented in future.

    All delimiter types, comments, line continuations and spaces handling in
    delimeters are supported.

Mozilla
    Mozilla files use '=' as a delimiter, are UTF-8 encoded and thus don't
    need \\u escaping.  Any \\U values will be converted to correct Unicode
    characters.

Strings
    Mac OS X strings files are implemented using
    `these <https://developer.apple.com/library/mac/#documentation/MacOSX/Conceptual/BPInternational/Articles/StringsFiles.html>`_
    `two <https://developer.apple.com/library/mac/#documentation/Cocoa/Conceptual/LoadingResources/Strings/Strings.html>`_
    articles as references.

Flex
    Adobe Flex files seem to be normal .properties files but in UTF-8 just like
    Mozilla files. This
    `page <http://livedocs.adobe.com/flex/3/html/help.html?content=l10n_3.html>`_
    provides the information used to implement the dialect.

Skype
    Skype .lang files seem to be UTF-16 encoded .properties files.

XWiki
    XWiki translations files are standard Java .properties but with specific escaping
    support for simple quotes, and support of missing translations.
    This
    `XWiki document <https://dev.xwiki.org/xwiki/bin/view/Community/XWiki%20Translations%20Formats/>`_
    provides the information used to implement the dialect.

A simple summary of what is permissible follows.

Comments supported:

.. code-block:: properties

   # a comment
   // a comment (only at the beginning of a line)

   # The following are # escaped to render in docs
   # ! is standard but not widely supported
   #! a comment
   # /* is non-standard but used on some implementations
   #/* a comment (not across multiple lines) */


Name and Value pairs:

.. code-block:: properties

   # Delimiters
   key = value
   key : value
   # Whitespace delimiter
   # key[sp]value

   # Space in key and around value
   \ key\ = \ value

   # Note that the b and c are escaped for reST rendering
   b = a string with escape sequences \\t \\n \\r \\\\ \\" \\' \\ (space) \u0123
   c = a string with a continuation line \\
       continuation line

   # Special cases
   # key with no value
   //key (escaped; doesn't render in docs)
   # value no key (extractable in prop2po but not mergeable in po2prop)
   =value

   # .strings specific
   "key" = "value";

"""

from __future__ import annotations

import re
from codecs import iterencode
from copy import deepcopy

from lxml import etree

from translate.lang import data
from translate.misc import quote
from translate.misc.multistring import multistring
from translate.storage import base

labelsuffixes = (".label", ".title")
"""Label suffixes: entries with this suffix are able to be comibed with accesskeys
found in in entries ending with :attr:`.accesskeysuffixes`"""
accesskeysuffixes = (".accesskey", ".accessKey", ".akey")
"""Accesskey Suffixes: entries with this suffix may be combined with labels
ending in :attr:`.labelsuffixes` into accelerator notation"""


# the rstripeols convert dos <-> unix nicely as well
# output will be appropriate for the platform

eol = "\n"


def is_line_continuation(line):
    r"""
    Determine whether *line* has a line continuation marker.

    .properties files can be terminated with a backslash (\\) indicating
    that the 'value' continues on the next line.  Continuation is only
    valid if there are an odd number of backslashses (an even number
    would result in a set of N/2 slashes not an escape)

    :param line: A properties line
    :type line: str
    :return: Does *line* end with a line continuation
    :rtype: Boolean
    """
    pos = -1
    count = 0
    if len(line) == 0:
        return False
    # Count the slashes from the end of the line. Ensure we don't
    # go into infinite loop.
    while len(line) >= -pos and line[pos:][0] == "\\":
        pos -= 1
        count += 1
    return (count % 2) == 1  # Odd is a line continuation, even is not


def get_comment_one_line(line):
    """
    Determine whether a *line* is a one-line comment.

    :param line: A properties line
    :type line: unicode
    :return: True if line is a one-line comment
    :rtype: bool
    """
    stripped = line.strip()
    line_starters = ("#", "!", "//", ";")
    for starter in line_starters:
        if stripped.startswith(starter):
            return stripped[len(starter) :].strip()
    if stripped.startswith("/*") and stripped.endswith("*/"):
        return stripped[2:-2].strip()
    return None


def get_comment_start(line):
    """
    Determine whether a *line* starts a new multi-line comment.

    :param line: A properties line
    :type line: unicode
    :return: True if line starts a new multi-line comment
    :rtype: bool
    """
    stripped = line.strip()
    if stripped.startswith("/*") and not stripped.endswith("*/"):
        return line[2:].strip()
    return None


def get_comment_end(line):
    """
    Determine whether a *line* ends a new multi-line comment.

    :param line: A properties line
    :type line: unicode
    :return: True if line ends a new multi-line comment
    :rtype: bool
    """
    stripped = line.strip()
    if not stripped.startswith("/*") and stripped.endswith("*/"):
        return line[:-2].strip()
    return None


def _key_strip(key):
    """
    Cleanup whitespace found around a key.

    :param key: A properties key
    :type key: str
    :return: Key without any unneeded whitespace
    :rtype: str
    """
    newkey = key.rstrip()
    # If string now ends in \ we put back the whitespace that was escaped
    if newkey[-1:] == "\\":
        newkey += key[len(newkey) : len(newkey) + 1]
    return newkey.lstrip()


dialects = {}
default_dialect = "java"


def register_dialect(dialect):
    """Decorator that registers the dialect."""
    dialects[dialect.name] = dialect
    return dialect


def get_dialect(dialect=default_dialect):
    return dialects.get(dialect)


class Dialect:
    """Settings for the various behaviours in key=value files."""

    name = None
    default_encoding = "iso-8859-1"
    delimiters: list[str] = []
    pair_terminator = ""
    key_wrap_char = ""
    value_wrap_char = ""
    drop_comments = []
    has_plurals = False

    @staticmethod
    def encode(string, encoding=None):
        """Encode the string."""
        # FIXME: dialects are a bad idea, not possible for subclasses
        # to override key methods
        if encoding not in {"utf-8", "utf-16"}:
            return quote.javapropertiesencode(string or "")
        return quote.java_utf8_properties_encode(string or "")

    @staticmethod
    def decode(string):
        return quote.propertiesdecode(string)

    @classmethod
    def find_delimiter(cls, line):
        """
        Find the type and position of the delimiter in a property line.

        Property files can be delimited by "=", ":" or whitespace (space for now).
        We find the position of each delimiter, then find the one that appears
        first.

        :param line: A properties line
        :type line: str
        :param delimiters: valid delimiters
        :type delimiters: list
        :return: delimiter character and offset within *line*
        :rtype: Tuple (delimiter char, Offset Integer)
        """
        delimiter_dict = {}
        for delimiter in cls.delimiters:
            delimiter_dict[delimiter] = -1
        delimiters = delimiter_dict
        # Figure out starting position
        start_pos = len(line) - len(line.lstrip())  # Skip initial whitespace
        if cls.key_wrap_char and line[start_pos] == cls.key_wrap_char:
            # Skip the key if it is delimited by some char
            start_pos += 1
            while line[start_pos] != cls.key_wrap_char or line[start_pos - 1] == "\\":
                start_pos += 1
        # Find the position of each delimiter type
        for delimiter in delimiters:
            pos = line.find(delimiter, start_pos)
            while pos != -1:
                if delimiters[delimiter] == -1 and line[pos - 1] != "\\":
                    delimiters[delimiter] = pos
                    break
                pos = line.find(delimiter, pos + 1)
        # Find the first delimiter
        mindelimiter = None
        minpos = -1
        for delimiter, pos in delimiters.items():
            if pos == -1 or delimiter == " ":
                continue
            if minpos == -1 or pos < minpos:
                minpos = pos
                mindelimiter = delimiter
        if mindelimiter is None and delimiters.get(" ", -1) != -1:
            # Use space delimiter if we found nothing else
            return (" ", delimiters[" "])
        if (
            mindelimiter is not None
            and " " in delimiters
            and delimiters[" "] < delimiters[mindelimiter]
        ):
            # If space delimiter occurs earlier than ":" or "=" then it is the
            # delimiter only if there are non-whitespace characters between it and
            # the other detected delimiter.
            if len(line[delimiters[" "] : delimiters[mindelimiter]].strip()) > 0:
                return (" ", delimiters[" "])
        return (mindelimiter, minpos)

    @staticmethod
    def key_strip(key):
        """Strip unneeded characters from the key."""
        return _key_strip(key)

    @staticmethod
    def value_strip(value):
        """Strip unneeded characters from the value."""
        return value.lstrip()

    @staticmethod
    def is_line_continuation(line):
        return is_line_continuation(line)

    @staticmethod
    def strip_line_continuation(value):
        return value[:-1]

    @staticmethod
    def get_key_cldr_name(key):
        return (key, "other")

    @staticmethod
    def get_cldr_names_order():
        return ["other"]


@register_dialect
class DialectJava(Dialect):
    name = "java"
    default_encoding = "iso-8859-1"
    delimiters = ["=", ":", " "]


@register_dialect
class DialectJavaUtf8(DialectJava):
    name = "java-utf8"
    default_encoding = "utf-8"
    delimiters = ["=", ":", " "]

    @staticmethod
    def encode(string, encoding=None):
        return quote.java_utf8_properties_encode(string or "")


@register_dialect
class DialectJavaUtf16(DialectJava):
    name = "java-utf16"
    default_encoding = "utf-16"
    delimiters = ["=", ":", " "]

    @staticmethod
    def encode(string, encoding=None):
        return quote.java_utf8_properties_encode(string or "")


@register_dialect
class DialectXWiki(DialectJava):
    """
    XWiki dialect is mainly a Java properties behaviour but with special handling of
    simple quotes: they are escaped by doubling them when an argument on the form "{X}"
    is provided, X being a number.
    """

    name = "xwiki"
    default_encoding = "iso-8859-1"
    delimiters = ["=", ":", " "]
    has_plurals = True

    @staticmethod
    def encode(string, encoding=None):
        return quote.xwiki_properties_encode(string or "", encoding)

    @staticmethod
    def decode(string):
        return quote.xwiki_properties_decode(string)


@register_dialect
class DialectFlex(DialectJava):
    name = "flex"
    default_encoding = "utf-8"


@register_dialect
class DialectMozilla(DialectJavaUtf8):
    name = "mozilla"
    delimiters = ["="]

    @staticmethod
    def encode(string, encoding=None):
        """Encode the string."""
        string = quote.java_utf8_properties_encode(string or "")
        return quote.mozillaescapemarginspaces(string or "")


@register_dialect
class DialectGaia(DialectMozilla):
    name = "gaia"
    delimiters = ["="]


@register_dialect
class DialectGwt(DialectJavaUtf8):
    plural_regex = re.compile(r"(.*?)(?:\[(.+)\])?")
    name = "gwt"
    delimiters = ["="]
    has_plurals = True

    gwt_plural_categories = [
        ("", "other"),
        ("none", "zero"),
        ("one", "one"),
        ("two", "two"),
        ("few", "few"),
        ("many", "many"),
    ]

    gwt2cldr = dict(gwt_plural_categories)
    cldr2gwt = {b: a for a, b in gwt_plural_categories}

    @classmethod
    def get_key_cldr_name(cls, key):
        match = cls.plural_regex.fullmatch(key)
        basekey = match.group(1)
        variant = match.group(2)
        if variant is None:
            variant = ""

        try:
            variant = cls.gwt2cldr[variant]
        except KeyError:
            return (key, "other")
        return (basekey, variant)

    @classmethod
    def get_cldr_names_order(cls):
        return [y for x, y in cls.gwt_plural_categories]

    @classmethod
    def get_key(cls, key, variant):
        variant = cls.cldr2gwt.get(variant)

        # Some sanity checks
        if not variant:
            raise ValueError(f'Key "{key}" variant "{variant}" is invalid')
        return f"{key}[{variant}]"

    @classmethod
    def encode(cls, string, encoding=None):
        if encoding not in {"utf-8", "utf-16"}:
            result = quote.javapropertiesencode(string or "")
        else:
            result = quote.java_utf8_properties_encode(string or "")
        return result.replace("'", "''")

    @classmethod
    def decode(cls, string):
        result = super().decode(string)
        return result.replace("''", "'")


@register_dialect
class DialectSkype(Dialect):
    name = "skype"
    default_encoding = "utf-16"
    delimiters = ["="]

    @staticmethod
    def encode(string, encoding=None):
        return quote.java_utf8_properties_encode(string or "")


@register_dialect
class DialectStrings(Dialect):
    name = "strings"
    default_encoding = "utf-16"
    delimiters = ["="]
    pair_terminator = ";"
    key_wrap_char = '"'
    value_wrap_char = '"'
    out_ending = ";"
    out_delimiter_wrappers = " "
    drop_comments = ["/* No comment provided by engineer. */"]
    encode_trans = str.maketrans(
        {
            "\\": "\\\\",
            "\n": r"\n",
            "\t": r"\t",
        }
    )

    @staticmethod
    def key_strip(key):
        """Strip unneeded characters from the key."""
        newkey = key.rstrip().rstrip('"')
        # If string now ends in \ we put back the char that was escaped
        if newkey[-1:] == "\\":
            newkey += key[len(newkey) : len(newkey) + 1]
        ret = newkey.lstrip().lstrip('"')
        return ret.replace('\\"', '"')

    @staticmethod
    def value_strip(value):
        """Strip unneeded characters from the value."""
        newvalue = value.rstrip().rstrip(";").rstrip('"')
        # If string now ends in \ we put back the char that was escaped
        if newvalue[-1:] == "\\":
            newvalue += value[len(newvalue) : len(newvalue) + 1]
        ret = newvalue.lstrip().lstrip('"')
        return ret.replace('\\"', '"')

    @classmethod
    def encode(cls, string, encoding=None):  # noqa: ARG003
        return string.translate(cls.encode_trans)

    @staticmethod
    def is_line_continuation(line):
        l = line.rstrip()
        return not l or l[-1] != ";"

    @staticmethod
    def strip_line_continuation(value):
        return value


@register_dialect
class DialectStringsUtf8(DialectStrings):
    name = "strings-utf8"
    default_encoding = "utf-8"


class proppluralunit(base.TranslationUnit):
    KEY = "other"

    def __init__(self, source="", personality="java"):
        """Construct a blank propunit."""
        self.personality = get_dialect(personality)
        super().__init__(source)
        self.units = {}
        self.name = ""

    @staticmethod
    def _get_language_mapping(lang):
        if lang:
            locale = lang.replace("_", "-").split("-")[0]
            return data.plural_tags.get(locale, data.plural_tags["en"])
        return None

    def _get_existing_mapping(self):
        existing = self.units.keys()
        return [key for key in data.cldr_plural_categories if key in existing]

    def _get_target_mapping(self):
        cldr_mapping = proppluralunit._get_language_mapping(self._store.targetlanguage)
        if cldr_mapping:
            return cldr_mapping
        return self._get_existing_mapping()

    def _get_source_mapping(self):
        cldr_mapping = proppluralunit._get_language_mapping(self._store.sourcelanguage)
        if cldr_mapping:
            return cldr_mapping
        return self._get_existing_mapping()

    def _get_units(self, mapping):
        ret = []
        if len(self.units) > 1:
            for name in mapping:
                if name not in self.units:
                    unit = propunit("", self.personality.name)
                    unit.name = self.personality.get_key(self.name, name)
                    self.units[name] = unit
                ret.append(self.units[name])
        else:
            ret.append(self.units[proppluralunit.KEY])
        return ret

    @staticmethod
    def _get_strings(strings, mapping):
        ret = []
        if len(strings) > 1:
            for i in range(len(mapping)):
                if i < len(strings):
                    ret.append(strings[i])
                else:
                    ret.append("")
        else:
            ret.append(strings[0])
        return ret

    def _get_source_unit(self):
        self._get_units(self._get_source_mapping())  # Generate missing forms
        return self.units[proppluralunit.KEY]

    def _get_ordered_units(self):
        # Used for str (GWT order)
        mapping = self._get_target_mapping()
        names = [
            name for name in self.personality.get_cldr_names_order() if name in mapping
        ]
        return self._get_units(names)

    def hasplural(self, key=None):
        if key is None:
            return len(self.units) > 1
        return key in self.units

    def settarget(self, text):
        mapping = None
        if isinstance(text, multistring):
            strings = text.strings
        elif isinstance(text, list):
            strings = text
        elif isinstance(text, dict):
            mapping, strings = map(list, zip(*text.items()))
        else:
            strings = [text]
        if mapping is None:
            mapping = self._get_target_mapping()

        strings = self._get_strings(strings, mapping)
        units = self._get_units(mapping)
        if len(strings) != len(units):
            raise ValueError(
                f'Not same plural counts between "{strings}" and "{units}"'
            )

        for a, b in zip(strings, units):
            b.target = a

    def gettarget(self):
        ll = [x.target for x in self._get_units(self._get_target_mapping())]
        if len(ll) > 1:
            return multistring(ll)
        return ll[0]

    target = property(gettarget, settarget)

    def getsource(self):
        ll = [x.source for x in self._get_units(self._get_source_mapping())]
        if len(ll) > 1:
            return multistring(ll)
        return ll[0]

    def setsource(self, text):
        mapping = None
        if isinstance(text, multistring):
            strings = text.strings
        elif isinstance(text, list):
            strings = text
        elif isinstance(text, dict):
            mapping, strings = tuple(map(list, zip(*text.items())))
        else:
            strings = [text]
        if mapping is None:
            mapping = self._get_source_mapping()

        strings = self._get_strings(strings, mapping)
        units = self._get_units(mapping)
        if len(strings) != len(units):
            raise ValueError(
                f'Not same plural counts between "{strings}" and "{units}"'
            )

        for a, b in zip(strings, units):
            b.source = a

    source = property(getsource, setsource)

    def getvalue(self):
        value = self._get_source_unit().value
        return multistring(value) if value is not None else None

    def setvalue(self, value):
        if isinstance(value, multistring):
            strings = value.strings
        elif isinstance(value, list):
            strings = value
        else:
            strings = [value]
        self._get_source_unit().value = strings[0]

    value = property(getvalue, setvalue)

    def getcomments(self):
        return self._get_source_unit().comments

    def setcomments(self, comments):
        self._get_source_unit().comments = comments

    comments = property(getcomments, setcomments)

    def getdelimiter(self):
        return self._get_source_unit().delimiter

    def setdelimiter(self, delimiter):
        self._get_source_unit().delimiter = delimiter

    delimiter = property(getdelimiter, setdelimiter)

    def getnotes(self, origin=None):
        return self._get_source_unit().getnotes(origin)

    def getlocations(self):
        return self._get_source_unit().getlocations()

    def add_unit(self, unit, variant):
        self.units[variant] = unit

    def isblank(self):
        """
        returns whether this is a blank element, containing only
        comments.
        """
        return not (self.name or self.value)

    def istranslatable(self):
        return bool(self.name)

    def getid(self):
        return self.name

    def setid(self, value):
        self.name = value

    @property
    def missing(self):
        return self._get_source_unit().missing

    @missing.setter
    def missing(self, missing):
        self._get_source_unit().missing = missing

    def __str__(self):
        """
        Convert to a string. Double check that unicode is handled
        somehow here.
        """
        return self.getoutput()

    def getoutput(self):
        return "".join(unit.getoutput() for unit in self._get_ordered_units())

    @property
    def encoding(self):
        if self._store:
            return self._store.encoding
        return self.personality.default_encoding


@register_dialect
class DialectJoomla(Dialect):
    name = "joomla"
    default_encoding = "utf-8"
    delimiters = ["="]
    out_delimiter_wrappers = ""
    encode_trans = str.maketrans(
        {
            "\n": r"\n",
            "\t": r"\t",
            '"': '"_QQ_"',
        }
    )

    @staticmethod
    def value_strip(value):
        """Strip unneeded characters from the value."""
        return value.strip()

    @classmethod
    def decode(cls, string):
        string = super().decode(string)
        if len(string) > 2 and string[0] == '"' and string[-1] == '"':
            string = string[1:-1]
        return string.replace('"_QQ_"', '"')

    @classmethod
    def encode(cls, string, encoding=None):  # noqa: ARG003
        """Encode the string."""
        if not string:
            return string
        return f'"{string.translate(cls.encode_trans)}"'


class propunit(base.TranslationUnit):
    """
    An element of a properties file i.e. a name and value, and any comments
    associated.
    """

    def __init__(self, source="", personality="java"):
        """Construct a blank propunit."""
        self.personality = get_dialect(personality)
        super().__init__(source)
        self.name = ""
        self.value = ""
        self.translation = ""
        self.delimiter = "="
        self.comments = []
        self.source = source
        # a pair of symbols to enclose delimiter on the output
        # (a " " can be used for the sake of convenience)
        self.out_delimiter_wrappers = getattr(
            self.personality, "out_delimiter_wrappers", ""
        )
        # symbol that should end every property sentence
        # (e.g. ";" is required for Mac OS X strings)
        self.out_ending = getattr(self.personality, "out_ending", "")
        self.explicitely_missing = False
        self.output_missing = False

    @property
    def missing(self):
        return self.explicitely_missing or (
            not bool(self.translation) and not bool(self.source)
        )

    @missing.setter
    def missing(self, missing):
        self.explicitely_missing = missing

    @staticmethod
    def get_missing_part():
        """Return the string representing a missing translation."""
        return ""

    @staticmethod
    def strip_missing_part(line):
        """Remove the missing prefix from the line."""
        return line

    @staticmethod
    def represents_missing(line):
        """The line represents a missing translation."""
        return False

    @property
    def source(self):
        return self.personality.decode(self.value)

    @source.setter
    def source(self, source):
        self._rich_source = None
        self.value = self.personality.encode(source or "", self.encoding)

    @property
    def target(self):
        return re.sub("\\\\ ", " ", self.personality.decode(self.translation))

    @target.setter
    def target(self, target):
        self._rich_target = None
        self.translation = self.personality.encode(target or "", self.encoding)
        self.explicitely_missing = not bool(target)

    @property
    def encoding(self):
        if self._store:
            return self._store.encoding
        return self.personality.default_encoding

    def __str__(self):
        """Convert to a string."""
        return self.getoutput()

    def getoutput(self):
        """Convert the element back into formatted lines for a .properties file."""
        notes = "\n".join(self.comments)
        if notes:
            notes = f"{notes}\n"
        if self.isblank():
            return notes or "\n"
        # encode key, if needed
        key = self.name
        kwc = self.personality.key_wrap_char
        if kwc:
            key = key.replace(kwc, f"\\{kwc}")
            key = f"{kwc}{key}{kwc}"
        # encode value, if needed
        value = self.translation or self.value
        vwc = self.personality.value_wrap_char
        if vwc:
            value = value.replace(vwc, f"\\{vwc}")
            value = f"{vwc}{value}{vwc}"
        wrappers = self.out_delimiter_wrappers
        delimiter = f"{wrappers}{self.delimiter}{wrappers}"
        ending = self.out_ending
        missing_prefix = ""
        if self.output_missing and self.missing:
            missing_prefix = self.get_missing_part()
        return f"{notes}{missing_prefix}{key}{delimiter}{value}{ending}\n"

    def getlocations(self):
        return [self.name]

    def addnote(self, text, origin=None, position="append"):
        if origin in {"programmer", "developer", "source code", None}:
            if get_comment_one_line(text) is None and get_comment_start(text) is None:
                text = f"/* {text} */" if "\n" in text else f"// {text}"
            self.comments.append(text)
        else:
            super().addnote(text, origin=origin, position=position)

    def getnotes(self, origin=None):
        if origin in {"programmer", "developer", "source code", None}:
            output = []
            inmultilinecomment = False
            for line in self.comments:
                if (
                    not inmultilinecomment
                    and (parsed := get_comment_one_line(line)) is not None
                ):
                    output.append(parsed)
                elif (
                    not inmultilinecomment
                    and (parsed := get_comment_start(line)) is not None
                ):
                    output.append(parsed)
                    inmultilinecomment = True
                elif (
                    inmultilinecomment and (parsed := get_comment_end(line)) is not None
                ):
                    output.append(parsed)
                    inmultilinecomment = False
                else:
                    output.append(line)
            return "\n".join(output)
        return super().getnotes(origin)

    def removenotes(self, origin=None):
        self.comments = []

    def isblank(self):
        """Returns whether this is a blank element, containing only comments."""
        return not (self.name or self.value)

    def istranslatable(self):
        return bool(self.name)

    def getid(self):
        return self.name

    def setid(self, value):
        self.name = value


class xwikiunit(propunit):
    """
    Represents an XWiki translation unit. The difference with a propunit is twofold:
            1. the dialect used is xwiki for simple quote escape handling
            2. missing translations are output with a dedicated "### Missing: " prefix.
    """

    def __init__(self, source="", personality="xwiki"):
        super().__init__(source, personality)
        self.output_missing = True

    @staticmethod
    def get_missing_part():
        """Return the string representing a missing translation."""
        return "### Missing: "

    @classmethod
    def strip_missing_part(cls, line):
        """Remove the missing prefix from the line."""
        return line.replace(cls.get_missing_part(), "")

    @classmethod
    def represents_missing(cls, line):
        """Return true if the line represents a missing translation."""
        return line.startswith(cls.get_missing_part())


class propfile(base.TranslationStore):
    """this class represents a .properties file, made up of propunits."""

    UnitClass = propunit

    def __init__(self, inputfile=None, personality="java", encoding=None):
        """Construct a propfile, optionally reading in from inputfile."""
        super().__init__()
        self.personality = get_dialect(personality)
        self.encoding = encoding or self.personality.default_encoding
        self.filename = getattr(inputfile, "name", "")
        if inputfile is not None:
            propsrc = inputfile.read()
            inputfile.close()
            self.parse(propsrc)
            self.makeindex()

    def parse(self, propsrc):
        """Read the source of a properties file in and include them as units."""
        text, encoding = self.detect_encoding(
            propsrc,
            default_encodings=[self.personality.default_encoding, "utf-8", "utf-16"],
        )
        if not text and propsrc:
            raise OSError(
                "Cannot detect encoding for %s." % (self.filename or "given string")
            )
        self.encoding = encoding
        propsrc = text

        newunit = self.UnitClass("", self.personality.name)
        inmultilinevalue = False
        inmultilinecomment = False
        was_header = False

        for line in propsrc.split("\n"):
            # handle multiline value if we're in one
            line = quote.rstripeol(line)
            if inmultilinevalue:
                newunit.value += line.lstrip()
                # see if there's more
                inmultilinevalue = self.personality.is_line_continuation(newunit.value)
                # if we're still waiting for more...
                if inmultilinevalue:
                    newunit.value = self.personality.strip_line_continuation(
                        newunit.value
                    )
                if not inmultilinevalue:
                    # we're finished, add it to the list...
                    newunit.value = self.personality.value_strip(newunit.value)
                    self.addunit(newunit)
                    newunit = self.UnitClass("", self.personality.name)
            # otherwise, this could be a comment
            # FIXME handle // inline comments
            elif (
                inmultilinecomment
                or (one_line_comment := get_comment_one_line(line)) is not None
                or (comment_start := get_comment_start(line)) is not None
            ) and not self.UnitClass.represents_missing(line):
                # add a comment
                if line not in self.personality.drop_comments:
                    newunit.comments.append(line)

                if one_line_comment is not None:
                    pass
                elif not inmultilinecomment and comment_start is not None:
                    inmultilinecomment = True
                elif inmultilinecomment and get_comment_end(line) is not None:
                    inmultilinecomment = False
            elif not line.strip():
                # this is a blank line...
                # avoid adding comment only units
                if newunit.name:
                    self.addunit(newunit)
                    newunit = self.UnitClass("", self.personality.name)
                else:
                    newunit.comments.append("")

                if not was_header and str(newunit).strip():
                    self.addunit(newunit)
                    newunit = self.UnitClass("", self.personality.name)
                    was_header = True

            else:
                ismissing = False
                if self.UnitClass.represents_missing(line):
                    line = self.UnitClass.strip_missing_part(line)
                    ismissing = True
                newunit.delimiter, delimiter_pos = self.personality.find_delimiter(line)
                if delimiter_pos == -1:
                    newunit.name = self.personality.key_strip(line)
                    newunit.value = ""
                    newunit.delimiter = ""
                    newunit.missing = ismissing
                    self.addunit(newunit)
                    newunit = self.UnitClass("", self.personality.name)
                else:
                    newunit.name = self.personality.key_strip(line[:delimiter_pos])
                    newunit.missing = ismissing
                    if self.personality.is_line_continuation(
                        line[delimiter_pos + 1 :].lstrip()
                    ):
                        inmultilinevalue = True
                        newunit.value = line[delimiter_pos + 1 :].lstrip()[:-1]
                        newunit.value = self.personality.strip_line_continuation(
                            line[delimiter_pos + 1 :].lstrip()
                        )
                    else:
                        newunit.value = self.personality.value_strip(
                            line[delimiter_pos + 1 :]
                        )
                        self.addunit(newunit)
                        newunit = self.UnitClass("", self.personality.name)
        # see if there is a leftover one...
        if inmultilinevalue or (
            len(newunit.comments) > 0
            and not (len(newunit.comments) == 1 and not (newunit.comments[0]))
        ):
            self.addunit(newunit)

        if self.personality.has_plurals:
            self.fold()

    def fold(self):
        old_units = self.units
        self.units = []
        plurals = {}
        for unit in old_units:
            if not unit.istranslatable():
                self.addunit(unit)
                continue
            (key, variant) = self.personality.get_key_cldr_name(unit.name)
            if key not in plurals or plurals[key].hasplural(variant):
                # Generate fake unit for each keys (MUST use None as source)
                new_unit = proppluralunit(None, self.personality.name)
                new_unit.name = key
                self.addunit(new_unit)
                plurals[key] = new_unit

            # Put the unit
            plurals[key].add_unit(unit, variant)

    def serialize(self, out):
        """Write the units back to file."""
        # Thanks to iterencode, a possible BOM is written only once
        for chunk in iterencode(
            (unit.getoutput() for unit in self.units), self.encoding
        ):
            out.write(chunk)


class xwikifile(propfile):
    Name = "XWiki Properties"
    Extensions = ["properties"]
    UnitClass = xwikiunit

    def __init__(self, *args, **kwargs):
        kwargs["personality"] = "xwiki"
        kwargs["encoding"] = "iso-8859-1"
        super().__init__(*args, **kwargs)


class javafile(propfile):
    Name = "Java Properties"
    Extensions = ["properties"]

    def __init__(self, *args, **kwargs):
        kwargs["personality"] = "java"
        kwargs["encoding"] = "auto"
        super().__init__(*args, **kwargs)


class javautf8file(propfile):
    Name = "Java Properties (UTF-8)"
    Extensions = ["properties"]

    def __init__(self, *args, **kwargs):
        kwargs["personality"] = "java-utf8"
        kwargs["encoding"] = "utf-8"
        super().__init__(*args, **kwargs)


class javautf16file(propfile):
    Name = "Java Properties (UTF-16)"
    Extensions = ["properties"]

    def __init__(self, *args, **kwargs):
        kwargs["personality"] = "java-utf16"
        kwargs["encoding"] = "utf-16"
        super().__init__(*args, **kwargs)


class gwtfile(propfile):
    Name = "Gwt Properties"
    Extensions = ["properties"]

    def __init__(self, *args, **kwargs):
        kwargs["personality"] = "gwt"
        kwargs["encoding"] = "utf-8"
        super().__init__(*args, **kwargs)


class stringsfile(propfile):
    Name = "OS X Strings"
    Extensions = ["strings"]

    def __init__(self, *args, **kwargs):
        kwargs["personality"] = "strings"
        super().__init__(*args, **kwargs)


class stringsutf8file(stringsfile):
    Name = "OS X Strings (UTF-8)"
    Extensions = ["strings"]

    def __init__(self, *args, **kwargs):
        kwargs["personality"] = "strings-utf8"
        kwargs["encoding"] = "utf-8"
        super().__init__(*args, **kwargs)


class joomlafile(propfile):
    Name = "Joomla Translations"
    Extensions = ["ini"]

    def __init__(self, *args, **kwargs):
        kwargs["personality"] = "joomla"
        super().__init__(*args, **kwargs)


class XWikiPageProperties(xwikifile):
    """
    Represents an XWiki Page containing translation properties as described in
    https://dev.xwiki.org/xwiki/bin/view/Community/XWiki%20Translations%20Formats/#HXWikiPageProperties.
    """

    Name = "XWiki Page Properties"
    Extensions = ["xml"]
    XML_HEADER = """<?xml version="1.1" encoding="UTF-8"?>

<!--
 * See the NOTICE file distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation; either version 2.1 of
 * the License, or (at your option) any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this software; if not, write to the Free
 * Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
 * 02110-1301 USA, or see the FSF site: http://www.fsf.org.
-->

"""

    XWIKI_BASIC_XML = """<xwikidoc>
    <translation>0</translation>
    <language/>
    <title/>
    <content/>
    </xwikidoc>
    """

    def __init__(self, *args, **kwargs):
        kwargs["personality"] = "xwiki"
        kwargs["encoding"] = "utf-8"
        self.root = None
        super(xwikifile, self).__init__(*args, **kwargs)

    def is_source_file(self):
        return self.getsourcelanguage() == self.gettargetlanguage()

    @staticmethod
    def get_parser():
        return etree.XMLParser(strip_cdata=False, resolve_entities=False)

    def extract_language(self):
        language_node = self.root.find("language")
        if language_node is not None and language_node.text:
            self.setsourcelanguage(language_node.text)
        else:
            language_node = self.root.find("defaultLanguage")
            if language_node is not None and language_node.text:
                self.setsourcelanguage(language_node.text)

    def parse(self, propsrc):
        if propsrc != b"\n":
            self.root = etree.XML(propsrc, self.get_parser())
            content = "".join(self.root.find("content").itertext())
            content = content.encode(self.encoding)
            self.extract_language()
            super().parse(content)

    def set_xwiki_xml_attributes(self, newroot):
        for child in newroot.findall("object"):
            newroot.remove(child)
        for child in newroot.findall("attachment"):
            newroot.remove(child)
        newroot.find("translation").text = "1"
        language_node = newroot.find("language")

        if self.gettargetlanguage():
            language_node.text = self.gettargetlanguage()
        else:
            language_node.text = self.getsourcelanguage()

        if language_node.text:
            newroot.set("locale", language_node.text)

    def write_xwiki_xml(self, newroot, out):
        xml_content = etree.tostring(newroot, encoding=self.encoding, method="xml")
        out.write(self.XML_HEADER.encode(self.encoding))
        out.write(xml_content)
        out.write(b"\n")

    def serialize(self, out):
        if self.root is None:
            self.root = etree.XML(self.XWIKI_BASIC_XML, self.get_parser())
        newroot = deepcopy(self.root)
        # We add a line break to ensure to have a line break before
        # closing of content tag.
        newroot.find("content").text = (
            "".join(unit.getoutput() for unit in self.units).strip() + "\n"
        )
        # We only modify the XML attributes if we are editing a translation file
        # if we are editing the source file we should not modify it.
        if not self.is_source_file():
            self.set_xwiki_xml_attributes(newroot)
            # We only want a single line break before the closing node.
            newroot.find("content").tail = "\n"
        self.write_xwiki_xml(newroot, out)


class XWikiFullPage(XWikiPageProperties):
    """
    Represents a full XWiki Page translation: this file does not contains properties
    but its whole content needs to be translated.
    More information on
    https://dev.xwiki.org/xwiki/bin/view/Community/XWiki%20Translations%20Formats/#HXWikiFullContentTranslation.
    """

    Name = "XWiki Full Page"

    def parse(self, propsrc):
        if propsrc != b"\n":
            self.root = etree.XML(propsrc, self.get_parser())
            content = "".join(self.root.find("content").itertext()).replace("\n", "\\n")
            title = "".join(self.root.find("title").itertext())
            forparsing = ""
            if content:
                forparsing += f"content={content}\n"
            if title:
                forparsing += f"title={title}\n"
            self.extract_language()
            super(XWikiPageProperties, self).parse(forparsing.encode(self.encoding))

    @staticmethod
    def output_unit(unit):
        value = unit.personality.encode(unit.source, unit.encoding)
        translation = unit.personality.encode(unit.target, unit.encoding)
        return translation or value

    def serialize(self, out):
        unit_title = self.findid("title")
        unit_content = self.findid("content")
        if self.root is None:
            self.root = etree.XML(self.XWIKI_BASIC_XML, self.get_parser())
        newroot = deepcopy(self.root)
        if unit_title is not None:
            newroot.find("title").text = self.output_unit(unit_title)
        if unit_content is not None:
            newroot.find("content").text = self.output_unit(unit_content).replace(
                "\\n", "\n"
            )
        # We only modify the XML attributes if we are editing a translation file
        # if we are editing the source file we should not modify it.
        if not self.is_source_file():
            self.set_xwiki_xml_attributes(newroot)
        self.write_xwiki_xml(newroot, out)
