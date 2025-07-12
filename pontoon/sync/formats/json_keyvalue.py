"""
Parser for key-value JSON, a nested Object structure of String values.
This implementation does not supports plurals.

Each key can be associated with either a String or an Object value.
Therefore, the format support nested values.

A key can contain any character.
Nested keys are internally stored as a JSON array.
"""

from __future__ import annotations

from datetime import datetime

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Message

from pontoon.base.models import Entity

from .common import VCSTranslation


def plain_json_as_translation(entry: Entry):
    return VCSTranslation(
        key=entry.id,
        string=serialize_message(Format.plain_json, entry.value) or None,
    )


def plain_json_as_entity(entry: Entry[Message], now: datetime) -> Entity:
    return Entity(
        key=list(entry.id),
        string=serialize_message(Format.plain_json, entry.value),
        date_created=now,
    )
