"""
Parser for the xliff translation format.
"""

from __future__ import annotations

from html import unescape
from re import compile

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Message, Resource, Section

from .common import VCSTranslation


note_re = compile(r"note\[\d+\]")


def parse(res: Resource[Message]):
    return [
        as_translation(order, section, entry)
        for order, (section, entry) in enumerate(
            (section, entry)
            for section in res.sections
            for entry in section.entries
            if isinstance(entry, Entry)
        )
    ]


def as_translation(order: int, section: Section, entry: Entry):
    assert len(section.id) == 1
    assert len(entry.id) == 1
    context = entry.id[0]
    key = section.id[0] + "\x04" + context
    string = unescape(serialize_message(Format.xliff, entry.value))
    comments: list[str] = [entry.comment] if entry.comment else []
    comments += [m.value for m in entry.meta if note_re.fullmatch(m.key)]
    return VCSTranslation(
        key=key,
        context=context,
        order=order,
        string=string or None,
        source_string=entry.get_meta("source") or "",
        comments=comments or None,
    )
