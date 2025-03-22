#
# Copyright 2002-2007 Zuza Software Foundation
# Copyright 2016 F Wolff
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
From the GNU gettext manual:
     WHITE-SPACE
     #  TRANSLATOR-COMMENTS
     #. AUTOMATIC-COMMENTS
     #| PREVIOUS MSGID                 (Gettext 0.16 - check if this is the correct position - not yet implemented)
     #: REFERENCE...
     #, FLAG...
     msgctxt CONTEXT                   (Gettext 0.15)
     msgid UNTRANSLATED-STRING
     msgstr TRANSLATED-STRING.
"""

import re

SINGLE_BYTE_ENCODING = "iso-8859-1"
isspace = str.isspace
find = str.find
rfind = str.rfind
startswith = str.startswith
append = list.append
decode = bytes.decode


class PoParseError(ValueError):
    def __init__(self, parse_state, message=None):
        self.parse_state = parse_state
        if message is None:
            message = "Syntax error"
        super().__init__(
            f"{message} on line {parse_state.lineno}: {parse_state.last_line!r}"
        )


class ParseState:
    def __init__(self, input_iterator, UnitClass, encoding=SINGLE_BYTE_ENCODING):
        # A single-byte encoding is first defined to be able to read the header
        # without risking UnicodeDecodeErrors. As soon as the header is parsed,
        # the encoding defined in the header is used for re-encoding the header
        # and for decoding all further strings.
        self._input_iterator = input_iterator
        self.next_line = ""
        self.last_line = ""
        self.lineno = 0
        self.eof = False
        self.encoding = encoding
        self.read_line()
        self.UnitClass = UnitClass

    def decode(self, string):
        if self.encoding is not None:
            return decode(string, self.encoding)
        return string

    def read_line(self):
        self.last_line = current = self.next_line
        if self.eof:
            return current
        try:
            self.next_line = next(self._input_iterator)
            self.lineno += 1
            while not self.eof and self.next_line.isspace():
                self.next_line = next(self._input_iterator)
                self.lineno += 1
        except StopIteration:
            self.next_line = ""
            self.eof = True
        else:
            if isinstance(self.next_line, bytes) and self.encoding is not None:
                self.next_line = decode(self.next_line, self.encoding)
        return current

    def new_input(self, _input):
        return ParseState(_input, self.UnitClass, self.encoding)


def read_prevmsgid_lines(parse_state):
    """
    Read all the lines belonging starting with #|. These lines contain the
    previous msgid and msgctxt info. We strip away the leading '#| ' and read
    until we stop seeing #|.
    """
    prevmsgid_lines = []
    next_line = parse_state.next_line
    while startswith(next_line, "#|") or startswith(next_line, "|"):
        content = parse_state.read_line()
        prefix_len = content.index("|") + 1
        while content[prefix_len] == " ":
            prefix_len += 1
        content = content[prefix_len:]
        append(prevmsgid_lines, content)
        next_line = parse_state.next_line
    return prevmsgid_lines


def parse_prev_msgctxt(parse_state, unit):
    parse_message(parse_state, "msgctxt", 7, unit.prev_msgctxt)
    return len(unit.prev_msgctxt) > 0


def parse_prev_msgid(parse_state, unit):
    parse_message(parse_state, "msgid", 5, unit.prev_msgid)
    return len(unit.prev_msgid) > 0


def parse_prev_msgid_plural(parse_state, unit):
    parse_message(parse_state, "msgid_plural", 12, unit.prev_msgid_plural)
    return len(unit.prev_msgid_plural) > 0


def parse_comment(parse_state, unit):
    next_line = parse_state.next_line.lstrip()
    if next_line and next_line[0] in {"#", "|"}:
        next_char = next_line[1]
        if next_char == ".":
            append(unit.automaticcomments, next_line)
        elif next_line[0] == "|" or next_char == "|":
            parsed = False
            # Read all the lines starting with #|
            prevmsgid_lines = read_prevmsgid_lines(parse_state)
            # Create a parse state object that holds these lines
            ps = parse_state.new_input(iter(prevmsgid_lines))
            # Parse the msgctxt if any
            parsed |= parse_prev_msgctxt(ps, unit)
            # Parse the msgid if any
            parsed |= parse_prev_msgid(ps, unit)
            # Parse the msgid_plural if any
            parsed |= parse_prev_msgid_plural(ps, unit)
            # Fail with error in csae nothing was parsed
            if not parsed:
                raise PoParseError(parse_state)
            return parse_state.next_line
        elif next_char == ":":
            append(unit.sourcecomments, next_line)
        elif next_char == ",":
            append(unit.typecomments, next_line)
        elif next_char == "~":
            # Special case: we refuse to parse obsoletes: they are done
            # elsewhere to ensure we reuse the normal unit parsing code
            return None
        else:
            append(unit.othercomments, next_line)
        return parse_state.read_line()
    return None


def parse_comments(parse_state, unit):
    if not parse_comment(parse_state, unit):
        return None
    while parse_comment(parse_state, unit):
        pass
    return True


def read_obsolete_lines(parse_state):
    """Read all the lines belonging to the current unit if obsolete."""
    obsolete_lines = []
    next_line = parse_state.next_line
    while startswith(next_line, "#~"):
        content = parse_state.read_line()[2:].lstrip()
        append(obsolete_lines, content)
        next_line = parse_state.next_line
        if startswith(content, "msgstr"):
            # now we saw a msgstr, so we need to become more conservative to
            # avoid parsing into the following unit
            while startswith(next_line, '#~ "') or startswith(next_line, "#~ msgstr"):
                content = parse_state.read_line()[3:]
                append(obsolete_lines, content)
                next_line = parse_state.next_line
            break
    return obsolete_lines


def parse_obsolete(parse_state, unit):
    obsolete_lines = read_obsolete_lines(parse_state)
    if len(obsolete_lines) == 0:
        return None
    unit = parse_unit(parse_state.new_input(iter(obsolete_lines)), unit)
    if unit is not None:
        unit.makeobsolete()
    return unit


def parse_quoted(parse_state, start_pos=0):
    line = parse_state.next_line
    left = find(line, '"', start_pos)
    if left == start_pos or isspace(line[start_pos:left]):
        right = rfind(line, '"')
        if left != right:
            return parse_state.read_line()[left : right + 1]
        raise PoParseError(parse_state, "end-of-line within string")
    return None


def parse_msg_comment(parse_state, msg_comment_list, string):
    while string is not None:
        append(msg_comment_list, string)
        if find(string, "\\n") > -1:
            return parse_quoted(parse_state)
        string = parse_quoted(parse_state)
    return None


def parse_multiple_quoted(parse_state, msg_list, msg_comment_list, first_start_pos=0):
    string = parse_quoted(parse_state, first_start_pos)
    while string is not None:
        if msg_comment_list is None or not startswith(string, '"_:'):
            append(msg_list, string)
            string = parse_quoted(parse_state)
        else:
            string = parse_msg_comment(parse_state, msg_comment_list, string)


def parse_message(
    parse_state, start_of_string, start_of_string_len, msg_list, msg_comment_list=None
):
    if startswith(parse_state.next_line, start_of_string):
        return parse_multiple_quoted(
            parse_state, msg_list, msg_comment_list, start_of_string_len
        )
    return None


def parse_msgctxt(parse_state, unit):
    parse_message(parse_state, "msgctxt", 7, unit.msgctxt)
    return len(unit.msgctxt) > 0


def parse_msgid(parse_state, unit):
    parse_message(parse_state, "msgid", 5, unit.msgid, unit.msgidcomments)
    return len(unit.msgid) > 0 or len(unit.msgidcomments) > 0


def parse_msgstr(parse_state, unit):
    parse_message(parse_state, "msgstr", 6, unit.msgstr)
    return len(unit.msgstr) > 0


def parse_msgid_plural(parse_state, unit):
    parse_message(
        parse_state, "msgid_plural", 12, unit.msgid_plural, unit.msgid_pluralcomments
    )
    return len(unit.msgid_plural) > 0 or len(unit.msgid_pluralcomments) > 0


MSGSTR_ARRAY_ENTRY_LEN = len("msgstr[")


def add_to_dict(msgstr_dict, line, right_bracket_pos, entry):
    index = int(line[MSGSTR_ARRAY_ENTRY_LEN:right_bracket_pos])
    if index not in msgstr_dict:
        msgstr_dict[index] = []
    msgstr_dict[index].extend(entry)


def get_entry(parse_state, right_bracket_pos):
    entry = []
    parse_message(parse_state, "msgstr[", right_bracket_pos + 1, entry)
    return entry


def parse_msgstr_array_entry(parse_state, msgstr_dict):
    line = parse_state.next_line
    right_bracket_pos = find(line, "]", MSGSTR_ARRAY_ENTRY_LEN)
    if right_bracket_pos >= 0:
        entry = get_entry(parse_state, right_bracket_pos)
        if entry:
            add_to_dict(msgstr_dict, line, right_bracket_pos, entry)
            return True
        return False
    return False


def parse_msgstr_array(parse_state, unit):
    msgstr_dict = {}
    result = parse_msgstr_array_entry(parse_state, msgstr_dict)
    if not result:  # We require at least one result
        return False
    while parse_msgstr_array_entry(parse_state, msgstr_dict):
        pass
    unit.msgstr = msgstr_dict
    return True


def parse_plural(parse_state, unit):
    return bool(
        parse_msgid_plural(parse_state, unit) and parse_msgstr_array(parse_state, unit)
    )


def parse_msg_entries(parse_state, unit):
    parse_msgctxt(parse_state, unit)
    return bool(
        parse_msgid(parse_state, unit)
        and (parse_msgstr(parse_state, unit) or parse_plural(parse_state, unit))
    )


def parse_unit(parse_state, unit=None):
    unit = unit or parse_state.UnitClass()
    parsed_comments = parse_comments(parse_state, unit)
    obsolete_unit = parse_obsolete(parse_state, unit)
    if obsolete_unit is not None:
        return obsolete_unit
    parsed_msg_entries = parse_msg_entries(parse_state, unit)
    if parsed_comments or parsed_msg_entries:
        return unit
    return None


def set_encoding(parse_state, store, unit):
    charset = None
    if (
        isinstance(unit.msgstr, list)
        and unit.msgstr
        and isinstance(unit.msgstr[0], str)
    ):
        charset = re.search("charset=([^\\s\\\\n]+)", "".join(unit.msgstr))
    if charset:
        encoding = charset.group(1)
        if encoding != "CHARSET":
            store._encoding = encoding
        else:
            store._encoding = "utf-8"
    else:
        store._encoding = "utf-8"
    parse_state.encoding = store._encoding


def decode_list(lst, decode):
    return [decode(item.encode(SINGLE_BYTE_ENCODING)) for item in lst]


def decode_header(unit, decode):
    """
    The header has been arbitrarily decoded with a single-byte encoding. We
    re-encode it to decode values with the proper encoding defined in the header
    (using decode_list above).
    """
    for attr in (
        "msgctxt",
        "msgid",
        "msgid_pluralcomments",
        "msgid_plural",
        "msgstr",
        "othercomments",
        "automaticcomments",
        "sourcecomments",
        "typecomments",
        "msgidcomments",
    ):
        element = getattr(unit, attr)
        if isinstance(element, list):
            setattr(unit, attr, decode_list(element, decode))
        else:
            setattr(
                unit,
                attr,
                {key: decode_list(value, decode) for key, value in element.items()},
            )


def parse_header(parse_state, store):
    first_unit = parse_unit(parse_state)
    if first_unit is None:
        return None
    set_encoding(parse_state, store, first_unit)
    decode_header(first_unit, parse_state.decode)
    # Fix encoding of next line in parser
    # It was originally parsed with  SINGLE_BYTE_ENCODING
    # but we need to convert it to actual encoding
    parse_state.next_line = parse_state.decode(
        parse_state.next_line.encode(SINGLE_BYTE_ENCODING)
    )
    return first_unit


def parse_units(parse_state, store):
    unit = parse_header(parse_state, store)
    while unit:
        unit.infer_state()
        store.addunit(unit)
        unit = parse_unit(parse_state)
    if not parse_state.eof:
        raise PoParseError(parse_state)
