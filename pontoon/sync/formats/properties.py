"""
Parser for the strings.xml file format.
"""

from __future__ import annotations

from datetime import datetime
from re import Match, compile

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Message

from pontoon.base.models import Entity

from .common import VCSTranslation


esc_u = compile(r"(?<!\\)\\u(?!0000)[0-9A-Fa-f]{4}")
esc_ws = compile(r"(?<!\\)\\([^\S\n])")


def _prop_unescape(m: Match[str]):
    return m[0].encode("utf-8").decode("unicode_escape")


def _string(entry: Entry[Message]):
    string = serialize_message(Format.properties, entry.value)
    string = esc_u.sub(_prop_unescape, string)
    string = esc_ws.sub(r"\1", string)
    return string


def properties_as_translation(entry: Entry[Message]):
    return VCSTranslation(key=entry.id, string=_string(entry))


def properties_as_entity(entry: Entry[Message], now: datetime) -> Entity:
    return Entity(
        new_key=list(entry.id),
        string=_string(entry),
        comment=entry.comment,
        date_created=now,
    )
