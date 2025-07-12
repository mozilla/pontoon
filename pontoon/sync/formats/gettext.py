from datetime import datetime

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import (
    CatchallKey,
    Entry,
    Expression,
    Message,
    PatternMessage,
    SelectMessage,
    VariableRef,
)

from pontoon.base.models import Entity

from .common import VCSTranslation


def gettext_as_translation(entry: Entry[Message]):
    if isinstance(entry.value, SelectMessage) and all(
        not pattern or pattern == [""] for pattern in entry.value.variants.values()
    ):
        string = None
    else:
        string = serialize_message(Format.mf2, entry.value) or None
    fuzzy = any(m.key == "flag" and m.value == "fuzzy" for m in entry.meta)
    return VCSTranslation(key=entry.id, string=string, fuzzy=fuzzy)


def gettext_as_entity(entry: Entry[Message], now: datetime) -> Entity:
    source_str = entry.id[0]
    plural_str = entry.get_meta("plural")
    source_msg = (
        PatternMessage([source_str])
        if plural_str is None
        else SelectMessage(
            declarations={"n": Expression(VariableRef("n"), "number")},
            selectors=(VariableRef("n"),),
            variants={("one",): [source_str], (CatchallKey("other"),): [plural_str]},
        )
    )

    return Entity(
        new_key=list(entry.id),
        string=serialize_message(Format.mf2, source_msg),
        comment=entry.get_meta("extracted-comments") or "",
        source=[tuple(m.value.split(":")) for m in entry.meta if m.key == "reference"],
        date_created=now,
    )
