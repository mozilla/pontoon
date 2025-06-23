"""
Parser for to pofile translation format.
"""

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import (
    CatchallKey,
    Entry,
    Expression,
    Message,
    PatternMessage,
    Resource,
    SelectMessage,
    VariableRef,
)

from .common import VCSTranslation


def parse(res: Resource[Message]):
    return [
        as_translation(order, entry)
        for order, entry in enumerate(res.all_entries())
        if entry.get_meta("obsolete") != "true"
    ]


def as_translation(order: int, entry: Entry[Message]):
    # Pofiles use the source as the key prepended with context if available.
    key = entry.id[0]
    context = entry.id[1] if len(entry.id) == 2 else ""
    if context:
        key = context + "\x04" + key
    string = serialize_message(Format.mf2, entry.value)
    comment = entry.get_meta("extracted-comments")

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

    return VCSTranslation(
        key=key,
        context=context,
        order=order,
        string=string or None,
        source_string=serialize_message(Format.mf2, source_msg),
        comments=comment.split("\n") if comment else None,
        fuzzy=any(m.key == "flag" and m.value == "fuzzy" for m in entry.meta),
        source=[tuple(m.value.split(":")) for m in entry.meta if m.key == "reference"]
        or None,
    )
