"""
Parser for the strings.xml file format.
"""

from __future__ import annotations

from datetime import datetime
from html import unescape
from re import compile

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Message

from pontoon.base.models import Entity

from .common import VCSTranslation


esc_u = compile(r"(?<!\\)\\u([0-9A-Fa-f]{4})")
esc_char = compile(r"(?<!\\)\\([^nt])")
esc_nl = compile(r"(?<!\\)\\n\s*")
ws_around_outer_tag = compile(r"^\s+(?=<)|(?<=>)\s+$")
ws_before_block = compile(r"\s+(?=<(br|label|li|p|/?ul)\b)")
ws_after_block = compile(r"((?<=<br>)|(?<=<br/>)|(?<=</ul>)|(?<=\\n))\s+")


def _string(entry: Entry[Message]):
    string = serialize_message(Format.android, entry.value)
    string = unescape(string)
    string = esc_u.sub(lambda m: chr(int(m[1], base=16)), string)
    string = esc_char.sub(r"\1", string)
    string = esc_nl.sub(r"\\n\n", string)
    string = ws_around_outer_tag.sub("", string)
    string = ws_before_block.sub("\n", string)
    string = ws_after_block.sub("\n", string)
    return string


def android_as_translation(entry: Entry[Message]):
    return VCSTranslation(key=entry.id, string=_string(entry))


def android_as_entity(entry: Entry[Message], now: datetime) -> Entity:
    return Entity(
        new_key=list(entry.id),
        string=_string(entry),
        comment=entry.comment,
        date_created=now,
    )
