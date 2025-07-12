"""
Parser for the xliff translation format.
"""

from __future__ import annotations

from datetime import datetime
from html import unescape
from re import compile

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Id as L10nId, Message

from pontoon.base.models import Entity

from .common import VCSTranslation


note_re = compile(r"note\[\d+\]")


def _key_and_context(section_id: L10nId, entry: Entry[Message]):
    assert len(section_id) == 1
    assert len(entry.id) == 1
    context = entry.id[0]
    key = section_id[0] + "\x04" + context
    return key, context


def xliff_as_translation(section_id: L10nId, entry: Entry):
    key, _ = _key_and_context(section_id, entry)
    string = unescape(serialize_message(Format.xliff, entry.value)) or None
    return VCSTranslation(key=key, string=string)


def xliff_as_entity(section_id: L10nId, entry: Entry[Message], now: datetime) -> Entity:
    key, context = _key_and_context(section_id, entry)
    comments: list[str] = [entry.comment] if entry.comment else []
    comments += [m.value for m in entry.meta if note_re.fullmatch(m.key)]
    return Entity(
        key=key,
        context=context,
        string=entry.get_meta("source") or "",
        comment="\n".join(comments),
        date_created=now,
    )
