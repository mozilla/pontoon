"""
Parser for key-value JSON, a nested Object structure of String values.
This implementation does not supports plurals.

Each key can be associated with either a String or an Object value.
Therefore, the format support nested values.

A key can contain any character.
Nested keys are internally stored as a JSON array.
"""

from __future__ import annotations

from json import dumps

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Message, Resource

from .common import VCSTranslation


def parse(res: Resource[Message]):
    return [
        as_translation(order, entry) for order, entry in enumerate(res.all_entries())
    ]


def as_translation(order: int, entry: Entry):
    string = serialize_message(Format.plain_json, entry.value)
    return VCSTranslation(
        key=dumps(entry.id),
        context=".".join(entry.id),
        order=order,
        strings={None: string} if (string) else {},
        source_string=string,
    )
