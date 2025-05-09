"""
Parser for the strings.xml file format.
"""

from __future__ import annotations

from html import unescape
from re import compile

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Message, Resource

from .common import VCSTranslation


def parse(res: Resource[Message]):
    return [
        as_translation(order, entry)
        for order, entry in enumerate(
            entry
            for section in res.sections
            if not section.id
            for entry in section.entries
            if isinstance(entry, Entry)
        )
    ]


esc_u = compile(r"(?<!\\)\\u[0-9]{4}")
esc_char = compile(r"(?<!\\)\\(.)")
ws_around_outer_tag = compile(r"^\s+(?=<)|(?<=>)\s+$")
ws_before_block = compile(r"\s+(?=<(br|label|li|p|/?ul)\b)")
ws_after_block = compile(r"((?<=<br>)|(?<=<br/>)|(?<=</ul>)|(?<=\\n))\s+")


def as_translation(order: int, entry: Entry[Message]):
    key = entry.id[0]
    string = serialize_message(Format.android, entry.value)
    string = unescape(string)
    string = esc_u.sub(lambda m: chr(int(m[1])), string)
    string = esc_char.sub(r"\1", string)
    string = ws_around_outer_tag.sub("", string)
    string = ws_before_block.sub("\n", string)
    string = ws_after_block.sub("\n", string)
    return VCSTranslation(
        key=key,
        context=key,
        order=order,
        strings={None: string},
        source_string=string,
        comments=entry.comment.split("\n") if entry.comment else None,
    )
