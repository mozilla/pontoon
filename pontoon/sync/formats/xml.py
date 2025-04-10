"""
Parser for the strings.xml file format.
"""

from __future__ import annotations

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


def as_translation(order: int, entry: Entry):
    key = entry.id[0]
    string = serialize_message(Format.android, entry.value).replace("\\'", "'")
    return VCSTranslation(
        key=key,
        context=key,
        order=order,
        strings={None: string} if string is not None else {},
        source_string=string,
        comments=entry.comment.split("\n") if entry.comment else None,
    )
