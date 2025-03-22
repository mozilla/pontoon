#
# Copyright 2004-2006,2008-2010 Zuza Software Foundation
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
Insert debug messages into XLIFF and Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/podebug.html
for examples and usage instructions.
"""

import os
import re
from functools import partial
from hashlib import md5

from translate.convert import dtd2po
from translate.storage import factory
from translate.storage.placeables import StringElem, general
from translate.storage.placeables import parse as rich_parse

format_re = re.compile("%[0-9c]*[sfFbBdh]")


def add_prefix(prefix, stringelems):
    for stringelem in stringelems:
        for string in stringelem.flatten():
            if len(string.sub) > 0:
                string.sub[0] = prefix + string.sub[0]
                break
    return stringelems


podebug_parsers = general.parsers
podebug_parsers.remove(general.CapsPlaceable.parse)
podebug_parsers.remove(general.CamelCasePlaceable.parse)


class podebug:
    def __init__(
        self,
        format=None,
        rewritestyle=None,
        ignoreoption=None,
        preserveplaceholders=False,
    ):
        if format is None:
            self.format = ""
        else:
            self.format = format
        self.rewritefunc = getattr(self, f"rewrite_{rewritestyle}", None)
        self.ignorefunc = getattr(self, f"ignore_{ignoreoption}", None)
        self.preserveplaceholders = preserveplaceholders

    @staticmethod
    def apply_to_translatables(string, func):
        """Applies func to all translatable strings in string."""
        string.map(
            lambda e: e.apply_to_strings(func),
            lambda e: e.isleaf() and e.istranslatable,
        )

    @classmethod
    def rewritelist(cls):
        return [
            rewrite.replace("rewrite_", "")
            for rewrite in dir(cls)
            if rewrite.startswith("rewrite_")
        ]

    @staticmethod
    def _rewrite_prepend_append(string, prepend, append=None):
        if append is None:
            append = prepend
        if not isinstance(string, StringElem):
            string = StringElem(string)
        string.sub.insert(0, prepend)
        if str(string).endswith("\n"):
            # Try and remove the last character from the tree
            try:
                lastnode = string.flatten()[-1]
                if isinstance(lastnode.sub[-1], str):
                    lastnode.sub[-1] = lastnode.sub[-1].rstrip("\n")
            except IndexError:
                pass
            string.sub.append(append + "\n")
        else:
            string.sub.append(append)
        return string

    def rewrite_xxx(self, string):
        return self._rewrite_prepend_append(string, "xxx")

    def rewrite_bracket(self, string):
        return self._rewrite_prepend_append(string, "[", "]")

    @staticmethod
    def rewrite_en(string):
        if not isinstance(string, StringElem):
            string = StringElem(string)
        return string

    @staticmethod
    def rewrite_blank(string):
        return StringElem("")

    def rewrite_chef(self, string):
        """Rewrite using Mock Swedish as made famous by Monty Python."""
        if not isinstance(string, StringElem):
            string = StringElem(string)
        # From Dive into Python which itself got it elsewhere
        # http://www.renderx.com/demos/examples/diveintopython.pdf
        subs = (
            (r"a([nu])", r"u\1"),
            (r"A([nu])", r"U\1"),
            (r"a\B", r"e"),
            (r"A\B", r"E"),
            (r"en\b", r"ee"),
            (r"\Bew", r"oo"),
            (r"\Be\b", r"e-a"),
            (r"\be", r"i"),
            (r"\bE", r"I"),
            (r"\Bf", r"ff"),
            (r"\Bir", r"ur"),
            (r"(\w*?)i(\w*?)$", r"\1ee\2"),
            (r"\bow", r"oo"),
            (r"\bo", r"oo"),
            (r"\bO", r"Oo"),
            (r"the", r"zee"),
            (r"The", r"Zee"),
            (r"th\b", r"t"),
            (r"\Btion", r"shun"),
            (r"\Bu", r"oo"),
            (r"\BU", r"Oo"),
            (r"v", r"f"),
            (r"V", r"F"),
            (r"w", r"w"),
            (r"W", r"W"),
            (r"([a-z])[.]", r"\1. Bork Bork Bork!"),
        )
        for a, b in subs:
            self.apply_to_translatables(string, partial(re.sub, a, b))
        return string

    PRESERVE_PLACEABLE_PARSERS = [
        general.UrlPlaceable.parse,
        general.EmailPlaceable.parse,
        general.XMLTagPlaceable.parse,
        general.DoubleAtPlaceable.parse,
        general.BracePlaceable.parse,
        general.PythonFormattingPlaceable.parse,
    ]
    # These parsers extract placeholders that should NOT be transformed during character-level rewrites
    # when the preserveplaceholders flag is True. It is not the full set of placeable parsers available
    # as some of them are not appropriate for this usage.

    def transform_characters_preserving_placeholders(self, s, transform):
        rich_string = rich_parse(s, self.PRESERVE_PLACEABLE_PARSERS)
        string_elements = rich_string.depth_first(filter=lambda e: e.isleaf())

        transformed = []

        for element in string_elements:
            if element.istranslatable:
                transformed.extend(transform(character) for character in str(element))
            else:
                transformed.append(element.sub[0])

        return "".join(transformed)

    REWRITE_UNICODE_MAP = (
        "ȦƁƇḒḖƑƓĦĪĴĶĿḾȠǾƤɊŘŞŦŬṼẆẊẎẐ" + "[\\]^_`" + "ȧƀƈḓḗƒɠħīĵķŀḿƞǿƥɋřşŧŭṽẇẋẏẑ"
    )

    def rewrite_unicode(self, string):
        """Convert to Unicode characters that look like the source string."""
        if not isinstance(string, StringElem):
            string = StringElem(string)

        def transpose(char):
            loc = ord(char) - 65
            if loc < 0 or loc > 56:
                return char
            return self.REWRITE_UNICODE_MAP[loc]

        def transformer(s):
            if self.preserveplaceholders:
                return self.transform_characters_preserving_placeholders(s, transpose)
            return "".join(transpose(c) for c in s)

        self.apply_to_translatables(string, transformer)
        return string

    REWRITE_FLIPPED_MAP = (
        "¡„#$%⅋,()⁎+´-˙/012Ɛᔭ59Ƚ86:;<=>¿@"
        "∀ԐↃᗡƎℲ⅁HIſӼ⅂WNOԀÒᴚS⊥∩ɅＭX⅄Z"
        "[\\]ᵥ_,"
        "ɐqɔpǝɟƃɥıɾʞʅɯuodbɹsʇnʌʍxʎz"
    )
    # Brackets should be swapped if the string will be reversed in memory.
    # If a right-to-left override is used, the brackets should be
    # unchanged.
    # Some alternatives:
    #  D: ᗡ◖
    #  K: Ж⋊Ӽ
    #  @: Ҩ - Seems only related in Dejavu Sans
    #  Q: Ὄ Ό Ὀ Ὃ Ὄ Ṑ Ò Ỏ
    #  _: ‾ - left out for now for the sake of GTK accelerators

    def rewrite_flipped(self, string):
        """Convert the string to look flipped upside down."""
        if not isinstance(string, StringElem):
            string = StringElem(string)

        def transpose(char):
            loc = ord(char) - 33
            if loc < 0 or loc > 89:
                return char
            return self.REWRITE_FLIPPED_MAP[loc]

        def transformer(s):
            if self.preserveplaceholders:
                return "\u202e" + self.transform_characters_preserving_placeholders(
                    s, transpose
                )
            return "\u202e" + "".join(transpose(c) for c in s)
            # To reverse instead of using the RTL override:
            # return ''.join(reversed([transpose(c) for c in s]))

        self.apply_to_translatables(string, transformer)
        return string

    def rewrite_classified(self, string):
        if not isinstance(string, StringElem):
            string = StringElem(string)

        def transpose(char):
            if char.isalnum():
                return "▮"
            return char

        def transformer(s):
            if self.preserveplaceholders:
                return self.transform_characters_preserving_placeholders(s, transpose)
            return "".join(transpose(c) for c in s)

        self.apply_to_translatables(string, transformer)
        return string

    @classmethod
    def ignorelist(cls):
        return [
            ignore.replace("ignore_", "")
            for ignore in dir(cls)
            if ignore.startswith("ignore_")
        ]

    @staticmethod
    def ignore_openoffice(unit):
        for location in unit.getlocations():
            if location.startswith("Common.xcu#..Common.View.Localisation"):
                return True
            if location.startswith("profile.lng#STR_DIR_MENU_NEW_"):
                return True
            if location.startswith("profile.lng#STR_DIR_MENU_WIZARD_"):
                return True
        return False

    def ignore_libreoffice(self, unit):
        return self.ignore_openoffice(unit)

    @staticmethod
    def ignore_mozilla(unit):
        locations = unit.getlocations()
        if len(locations) == 1 and locations[0].lower().endswith(".accesskey"):
            return True
        for location in locations:
            if dtd2po.is_css_entity(location):
                return True
            if location in {"brandShortName", "brandFullName", "vendorShortName"}:
                return True
            if location.lower().endswith(".commandkey") or location.endswith(".key"):
                return True
        return False

    @staticmethod
    def ignore_gtk(unit):
        return unit.source == "default:LTR"

    @staticmethod
    def ignore_kde(unit):
        return unit.source == "LTR"

    def convertunit(self, unit, prefix):
        if self.ignorefunc:
            if self.ignorefunc(unit):
                return unit
        if prefix.find("@hash_placeholder@") != -1:
            hashable = unit.getlocations()[0] if unit.getlocations() else unit.source
            prefix = prefix.replace(
                "@hash_placeholder@",
                md5(hashable.encode("utf-8")).hexdigest()[: self.hash_len],
            )
        rich_string = unit.rich_target if unit.istranslated() else unit.rich_source
        if not isinstance(rich_string, StringElem):
            rich_string = [
                rich_parse(string, podebug_parsers) for string in rich_string
            ]
        if self.rewritefunc:
            rewritten = [self.rewritefunc(string) for string in rich_string]
            if rewritten:
                rich_string = rewritten
        unit.rich_target = add_prefix(prefix, rich_string)
        return unit

    def convertstore(self, store):
        prefix = self.format
        for formatstr in format_re.findall(self.format):
            if formatstr.endswith("s"):
                formatted = self.shrinkfilename(store.filename)
            elif formatstr.endswith("f"):
                formatted = store.filename
                formatted = os.path.splitext(formatted)[0]
            elif formatstr.endswith("F"):
                formatted = store.filename
            elif formatstr.endswith("b"):
                formatted = os.path.basename(store.filename)
                formatted = os.path.splitext(formatted)[0]
            elif formatstr.endswith("B"):
                formatted = os.path.basename(store.filename)
            elif formatstr.endswith("d"):
                formatted = os.path.dirname(store.filename)
            elif formatstr.endswith("h"):
                try:
                    self.hash_len = int(
                        "".join(c for c in formatstr[1:-1] if c.isdigit())
                    )
                except ValueError:
                    self.hash_len = 4
                formatted = "@hash_placeholder@"
            else:
                continue
            formatoptions = formatstr[1:-1]
            if formatoptions and not formatstr.endswith("h"):
                if "c" in formatoptions and formatted:
                    formatted = formatted[0] + "".join(
                        c for c in formatted[1:] if c.lower() not in "aeiou"
                    )
                length = "".join(c for c in formatoptions if c.isdigit())
                if length:
                    formatted = formatted[: int(length)]
            prefix = prefix.replace(formatstr, formatted)
        for unit in store.units:
            if not unit.istranslatable():
                continue
            self.convertunit(unit, prefix)
        return store

    @staticmethod
    def shrinkfilename(filename):
        if filename.startswith("." + os.sep):
            filename = filename.replace("." + os.sep, "", 1)
        dirname = os.path.dirname(filename)
        dirparts = dirname.split(os.sep)
        if not dirparts:
            dirshrunk = ""
        else:
            dirshrunk = dirparts[0][:4] + "-"
            if len(dirparts) > 1:
                dirshrunk += "".join(dirpart[0] for dirpart in dirparts[1:]) + "-"
        baseshrunk = os.path.basename(filename)[:4]
        if "." in baseshrunk:
            baseshrunk = baseshrunk[: baseshrunk.find(".")]
        return dirshrunk + baseshrunk


def convertpo(
    inputfile,
    outputfile,
    templatefile,
    format=None,
    rewritestyle=None,
    ignoreoption=None,
    preserveplaceholders=None,
):
    """Reads in inputfile, changes it to have debug strings, writes to outputfile."""
    # note that templatefile is not used, but it is required by the converter...
    inputstore = factory.getobject(inputfile)
    if inputstore.isempty():
        return 0
    convertor = podebug(
        format=format,
        rewritestyle=rewritestyle,
        ignoreoption=ignoreoption,
        preserveplaceholders=preserveplaceholders,
    )
    outputstore = convertor.convertstore(inputstore)
    outputstore.serialize(outputfile)
    return 1


def main():
    from translate.convert import convert

    formats = {
        "po": ("po", convertpo),
        "pot": ("po", convertpo),
        "xlf": ("xlf", convertpo),
        "xliff": ("xliff", convertpo),
        "tmx": ("tmx", convertpo),
    }
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    # TODO: add documentation on format strings...
    parser.add_option(
        "-f", "--format", dest="format", default="", help="specify format string"
    )
    parser.add_option(
        "",
        "--rewrite",
        dest="rewritestyle",
        type="choice",
        choices=podebug.rewritelist(),
        metavar="STYLE",
        help="the translation rewrite style: {}".format(
            ", ".join(podebug.rewritelist())
        ),
    )
    parser.add_option(
        "",
        "--ignore",
        dest="ignoreoption",
        type="choice",
        choices=podebug.ignorelist(),
        metavar="APPLICATION",
        help="apply tagging ignore rules for the given application: {}".format(
            ", ".join(podebug.ignorelist())
        ),
    )
    parser.add_option(
        "",
        "--preserveplaceholders",
        dest="preserveplaceholders",
        default=False,
        action="store_true",
        help="attempt to exclude characters that are part of placeholders when performing character-level"
        " rewrites so that consuming applications can still use the placeholders to generate final "
        "output",
    )
    parser.passthrough.append("format")
    parser.passthrough.append("rewritestyle")
    parser.passthrough.append("ignoreoption")
    parser.passthrough.append("preserveplaceholders")
    parser.run()


if __name__ == "__main__":
    main()
