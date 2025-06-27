from __future__ import annotations

from datetime import datetime

from fluent.syntax import FluentSerializer
from moz.l10n.formats.fluent import fluent_astify_entry
from moz.l10n.model import Entry, Message, Resource, Section

from pontoon.base.models import Entity

from .common import VCSTranslation


serializer = FluentSerializer()


def _string(entry: Entry[Message]):
    # Do not store comments in the string column
    entry.comment = ""
    entry.meta = []
    return serializer.serialize_entry(fluent_astify_entry(entry))


def ftl_as_translation(entry: Entry[Message]):
    assert len(entry.id) == 1
    return VCSTranslation(key=entry.id[0], string=_string(entry))


def ftl_as_entity(
    res: Resource[Message],
    section: Section[Message],
    entry: Entry[Message],
    now: datetime,
) -> Entity:
    assert len(entry.id) == 1
    key = entry.id[0]
    comment = entry.comment
    return Entity(
        key=key,
        context=key,
        string=_string(entry),
        comment=comment,
        group_comment=section.comment,
        resource_comment=res.comment,
        date_created=now,
    )
