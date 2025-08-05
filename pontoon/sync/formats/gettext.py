from typing import Any

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
    if entry.value.is_empty():
        return None
    string = serialize_message(Format.mf2, entry.value)
    fuzzy = any(m.key == "flag" and m.value == "fuzzy" for m in entry.meta)
    return VCSTranslation(key=entry.id, string=string, fuzzy=fuzzy)


def gettext_as_entity(entry: Entry[Message], kwargs: dict[str, Any]) -> Entity:
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
        key=list(entry.id),
        string=serialize_message(Format.mf2, source_msg),
        comment=entry.comment,
        meta=[[m.key, m.value] for m in entry.meta],
        **kwargs,
    )
