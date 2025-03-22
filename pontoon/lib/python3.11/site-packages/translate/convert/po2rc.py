#
# Copyright 2002-2006,2008-2009 Zuza Software Foundation
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
Convert Gettext PO localization files back to Windows Resource (.rc) files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/rc2po.html
for examples and usage instructions.
"""

import codecs
from collections.abc import Iterable

from translate.convert import convert
from translate.storage import po, rc
from translate.storage.rc import (
    generate_menu_pre_name,
    generate_popup_caption_name,
    generate_popup_pre_name,
    rcfile,
)

BLOCK_START = "BEGIN"
BLOCK_END = "END"

EMPTY_LOCATION = ""


def is_iterable_but_not_string(o):
    """Check if object is iterable but not a string."""
    return isinstance(o, Iterable) and not isinstance(o, str)


class rerc:
    def __init__(self, templatefile, charset="utf-8", lang=None, sublang=None):
        self.templatecontent = templatefile.read()
        self.templatestore = rcfile()
        self.templatestore.charset = charset
        self.templatestore.parse(self.templatecontent)
        self.inputdict = {}
        self.charset = charset
        self.lang = lang
        self.sublang = sublang

    @staticmethod
    def convert_comment(addnl, comment):
        if not addnl:
            yield "    "
        # Strip extra \r from \r\n which is left in the comment by the parser
        comment = comment.removesuffix("\r")
        yield comment

    def convert_caption(self, toks, name):
        yield "CAPTION "

        msgid = toks.caption[1:-1]
        if msgid in self.inputdict:
            if name in self.inputdict[msgid]:
                yield '"' + self.inputdict[msgid][name] + '"'
            elif EMPTY_LOCATION in self.inputdict[msgid]:
                yield '"' + self.inputdict[msgid][EMPTY_LOCATION] + '"'
        else:
            yield toks.caption

    def convert_block_options(self, s, loc, toks, name=None):
        for option in toks:
            yield " "
            if option.language:
                yield from self.convert_language(s, loc, option)
            elif option.caption:
                yield from self.convert_caption(option, name)
            else:
                yield " ".join(option)

    def convert_dialog(self, s, loc, toks):
        yield toks.block_id[0]
        yield " "
        yield toks.block_type
        if toks.block_options:
            name = rc.generate_dialog_caption_name(toks.block_type, toks.block_id[0])
            yield from self.convert_block_options(s, loc, toks.block_options, name)

        yield self.templatestore.newline
        yield BLOCK_START
        yield self.templatestore.newline
        addnl = False

        for c in toks.controls:
            if isinstance(c, str):
                yield from self.convert_comment(addnl, c)
                addnl = True
                continue
            if addnl:
                yield self.templatestore.newline
                addnl = False
            yield "    "
            c0 = c[0]
            if len(c0[0]) >= 16:
                yield c0[0]
                # If more than 16 char, put it on a new line to align it.
                yield self.templatestore.newline + " " * (16 + 4)
            else:
                yield c0[0].ljust(16)

            tmp = []

            # collect initial quoted items to form msgid
            i = 1
            while isinstance(c[i], str) and c[i].startswith(("'", '"')):
                i += 1
            msgid = "".join(cn[1:-1] for cn in c[1:i])

            name = rc.generate_dialog_control_name(
                toks.block_type, toks.block_id[0], c.id_control[0], c[i]
            )

            # append translation if available, otherwise use as is
            if msgid in self.inputdict:
                if name in self.inputdict[msgid]:
                    tmp.append('"' + self.inputdict[msgid][name] + '"')
                elif EMPTY_LOCATION in self.inputdict[msgid]:
                    tmp.append('"' + self.inputdict[msgid][EMPTY_LOCATION] + '"')
            elif i > 1:
                tmp.append(" ".join(c[1:i]))

            # and the remaining items, comma separated
            for a in c[i:]:
                if is_iterable_but_not_string(a):
                    tmp.append(" | ".join(a))
                else:
                    tmp.append(a)

            yield ",".join(tmp)
            yield self.templatestore.newline

        if addnl:
            yield self.templatestore.newline
            addnl = False
        yield BLOCK_END

    def convert_string_table(self, s, loc, toks):
        yield toks[0]
        if toks.block_options:
            yield from self.convert_block_options(s, loc, toks.block_options)
        yield self.templatestore.newline
        yield BLOCK_START
        yield self.templatestore.newline

        addnl = False
        for c in toks.controls:
            if isinstance(c, str):
                yield from self.convert_comment(addnl, c)
                addnl = True
                continue
            if addnl:
                yield self.templatestore.newline
                addnl = False
            yield "    "
            c0 = c[0]
            if len(c0[0]) >= 24:
                yield c0[0]
                yield self.templatestore.newline + " " * (24 + 4)
            else:
                yield c0[0].ljust(24)

            name = rc.generate_stringtable_name(c0[0])
            msgid = "".join(cn[1:-1] for cn in c[1:])

            tmp = c[1:]
            if msgid in self.inputdict:
                if name in self.inputdict[msgid]:
                    tmp = ['"' + self.inputdict[msgid][name] + '"']
                elif EMPTY_LOCATION in self.inputdict[msgid]:
                    tmp = ['"' + self.inputdict[msgid][EMPTY_LOCATION] + '"']

            for part in tmp[:-1]:
                yield part
                yield self.templatestore.newline + " " * (24 + 4)
            yield tmp[-1]

            yield self.templatestore.newline

        if addnl:
            yield self.templatestore.newline
            addnl = False
        yield BLOCK_END

    def convert_language(self, s, loc, toks):
        yield "LANGUAGE "
        yield self.lang
        if self.sublang:
            yield ", "
            yield self.sublang

    def convert_popup(self, popup, pre_name, ident=1):
        identation = " " * (4 * ident)
        yield identation
        yield popup.block_type
        if popup.caption:
            yield " "
            yield popup.pre_caption
            name = generate_popup_caption_name(pre_name)
            msgid = popup.caption[1:-1]
            if msgid in self.inputdict:
                if name in self.inputdict[msgid]:
                    yield '"' + self.inputdict[msgid][name] + '"'
                elif EMPTY_LOCATION in self.inputdict[msgid]:
                    yield '"' + self.inputdict[msgid][EMPTY_LOCATION] + '"'
            else:
                yield popup.caption
        else:
            yield " "

        for value in popup.values_:
            yield ", "
            yield value
        yield from popup.post_caption  # The rest of the options
        yield self.templatestore.newline

        yield identation
        yield BLOCK_START
        yield self.templatestore.newline

        for element in popup.elements:
            if isinstance(element, str):
                yield from self.convert_comment(True, element)
                continue

            if element.block_type and element.block_type == "MENUITEM":
                yield identation
                yield "    MENUITEM"
                yield " "

                if element.values_ and len(element.values_) >= 2:
                    name = rc.generate_menuitem_name(
                        pre_name, element.block_type, element.values_[1]
                    )
                    msgid = element.values_[0][1:-1]
                    if msgid in self.inputdict:
                        if name in self.inputdict[msgid]:
                            element.values_[0] = '"' + self.inputdict[msgid][name] + '"'
                        elif EMPTY_LOCATION in self.inputdict[msgid]:
                            element.values_[0] = (
                                '"' + self.inputdict[msgid][EMPTY_LOCATION] + '"'
                            )

                    yield ", ".join(element.values_)
                elif element.values_[0] == "SEPARATOR":
                    yield "SEPARATOR"
                else:
                    raise NotImplementedError

                yield self.templatestore.newline

            elif element.popups:
                for sub_popup in element.popups:
                    yield from self.convert_popup(
                        sub_popup,
                        generate_popup_pre_name(pre_name, popup.caption[1:-1]),
                        ident + 1,
                    )
        yield identation
        yield BLOCK_END
        yield self.templatestore.newline

    def convert_menu(self, s, loc, toks):
        yield toks.block_id[0]
        yield " "
        yield toks.block_type

        yield from self.convert_block_options(s, loc, toks.block_options)
        yield self.templatestore.newline

        yield BLOCK_START
        yield self.templatestore.newline

        pre_name = generate_menu_pre_name(toks.block_type, toks.block_id[0])

        for p in toks.popups:
            yield from self.convert_popup(p, pre_name)

        yield BLOCK_END

    def translate_strings(self, s, loc, toks):
        """Change the strings in the toks by the ones in the translation."""
        if toks.language:
            # Recreate the language, but using the settings.
            return list(self.convert_language(s, loc, toks))

        if toks.block_type:
            if toks.block_type in {"DIALOGEX", "DIALOG"}:
                return list(self.convert_dialog(s, loc, toks))

            if toks.block_type == "STRINGTABLE":
                return list(self.convert_string_table(s, loc, toks))

            if toks.block_type in {"MENU", "MENUEX"}:
                return list(self.convert_menu(s, loc, toks))

        return toks

    def convertstore(self, inputstore, includefuzzy=False):
        self.makestoredict(inputstore, includefuzzy)
        statement = rc.rc_statement()
        statement.add_parse_action(self.translate_strings)
        return statement.transform_string(self.templatecontent.decode(self.charset))

    def makestoredict(self, store, includefuzzy=False):
        """Make a dictionary of the translations."""
        for unit in store.units:
            if includefuzzy or not unit.isfuzzy():
                rcstring = unit.target
                if len(rcstring.strip()) == 0:
                    rcstring = unit.source

                escaped_source = rc.escape_to_rc(unit.source)

                if not escaped_source:
                    continue

                if escaped_source not in self.inputdict:
                    self.inputdict[escaped_source] = {}

                if len(unit.getlocations()) == 0:
                    self.inputdict[escaped_source][EMPTY_LOCATION] = rc.escape_to_rc(
                        rcstring
                    )
                else:
                    for location in unit.getlocations():
                        self.inputdict[escaped_source][location] = rc.escape_to_rc(
                            rcstring
                        )


def convertrc(
    inputfile,
    outputfile,
    templatefile,
    includefuzzy=False,
    charset=None,
    lang=None,
    sublang=None,
    outputthreshold=None,
):
    inputstore = po.pofile(inputfile)

    if not convert.should_output_store(inputstore, outputthreshold):
        return False

    if not lang:
        raise ValueError("must specify a target language")
    if templatefile is None:
        raise ValueError("must have template file for rc files")
    convertor = rerc(templatefile, charset, lang, sublang)
    outputrclines = convertor.convertstore(inputstore, includefuzzy)
    try:
        outputfile.write(outputrclines.encode("cp1252"))
    except UnicodeEncodeError:
        outputfile.write(codecs.BOM_UTF16_LE)
        outputfile.write(outputrclines.encode("utf-16-le"))
    outputfile.close()
    templatefile.close()
    return 1


def main(argv=None):
    # handle command line options
    formats = {("po", "rc"): ("rc", convertrc)}
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    defaultcharset = "utf-8"
    parser.add_option(
        "",
        "--charset",
        dest="charset",
        default=defaultcharset,
        help=f"charset to use to decode the RC files (default: {defaultcharset})",
        metavar="CHARSET",
    )
    parser.add_option(
        "-l", "--lang", dest="lang", default=None, help="LANG entry", metavar="LANG"
    )
    defaultsublang = "SUBLANG_DEFAULT"
    parser.add_option(
        "",
        "--sublang",
        dest="sublang",
        default=defaultsublang,
        help=f"SUBLANG entry (default: {defaultsublang})",
        metavar="SUBLANG",
    )
    parser.passthrough.append("charset")
    parser.passthrough.append("lang")
    parser.passthrough.append("sublang")
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
