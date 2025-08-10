"""
Parser for the xliff translation format.
"""

from __future__ import annotations

from html import unescape
from typing import Any

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Id as L10nId, Message

from pontoon.base.models import Entity

from .common import VCSTranslation


def xliff_as_translation(section_id: L10nId, entry: Entry):
    string = unescape(serialize_message(Format.xliff, entry.value))
    return VCSTranslation(key=section_id + entry.id, string=string) if string else None


def xliff_as_entity(
    section_id: L10nId, entry: Entry[Message], kwargs: dict[str, Any]
) -> Entity:
    return Entity(
        key=list(section_id + entry.id),
        string=entry.get_meta("source") or "",
        comment=entry.comment,
        meta=[[m.key, m.value] for m in entry.meta],
        **kwargs,
    )
