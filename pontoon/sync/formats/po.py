"""
Parser for to pofile translation format.
"""

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import (
    CatchallKey,
    Entry,
    Message,
    PatternMessage,
    Resource,
    SelectMessage,
)

from .common import VCSTranslation


def parse(res: Resource[Message]):
    return [
        as_translation(order, entry)
        for order, entry in enumerate(res.all_entries())
        if entry.get_meta("obsolete") != "true"
    ]


def as_translation(order: int, entry: Entry):
    # Pofiles use the source as the key prepended with context if available.
    key = entry.id[0]
    context = entry.id[1] if len(entry.id) == 2 else ""
    if context:
        key = context + "\x04" + key

    msg = entry.value
    strings: dict[int | None, str]
    if isinstance(msg, SelectMessage):
        strings = {}
        for (vkey,), pattern in msg.variants.items():
            if isinstance(vkey, CatchallKey):
                assert isinstance(vkey.value, str)
                vkey = vkey.value
            string = serialize_message(Format.po, PatternMessage(pattern))
            if string:
                strings[int(vkey)] = string
    else:
        string = serialize_message(Format.po, msg)
        strings = {None: string} if string else {}

    comment = entry.get_meta("extracted-comments")
    return VCSTranslation(
        key=key,
        context=context,
        order=order,
        strings=strings,
        source_string=entry.id[0],
        source_string_plural=entry.get_meta("plural") or "",
        comments=comment.split("\n") if comment else None,
        fuzzy=any(m.key == "flag" and m.value == "fuzzy" for m in entry.meta),
        source=[tuple(m.value.split(":")) for m in entry.meta if m.key == "reference"]
        or None,
    )
