from __future__ import annotations

from datetime import datetime

from fluent.syntax import FluentSerializer
from moz.l10n.formats.fluent import fluent_astify_entry
from moz.l10n.model import Entry, Message

from pontoon.base.models import Entity

from .common import VCSTranslation


serializer = FluentSerializer()


def _string(entry: Entry[Message]):
    # Do not store comments in the string field
    return serializer.serialize_entry(fluent_astify_entry(entry, lambda _: ""))


def ftl_as_translation(entry: Entry[Message]):
    return VCSTranslation(key=entry.id, string=_string(entry))


def ftl_as_entity(entry: Entry[Message], now: datetime) -> Entity:
    return Entity(
        key=list(entry.id),
        string=_string(entry),
        date_created=now,
    )
