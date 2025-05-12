"""
Parser for the strings.xml file format.
"""

from __future__ import annotations

from re import Match, compile

from moz.l10n.formats import Format
from moz.l10n.message import serialize_message
from moz.l10n.model import Entry, Message, Resource

from .common import VCSTranslation


def parse(res: Resource[Message]):
    return [
        as_translation(order, entry) for order, entry in enumerate(res.all_entries())
    ]


esc_u = compile(r"(?<!\\)\\u(?!0000)[0-9A-Fa-f]{4}")
esc_ws = compile(r"(?<!\\)\\([^\S\n])")


def prop_unescape(m: Match[str]):
    return m[0].encode("utf-8").decode("unicode_escape")


def as_translation(order: int, entry: Entry[Message]):
    key = entry.id[0]
    string = serialize_message(Format.properties, entry.value)
    string = esc_u.sub(prop_unescape, string)
    string = esc_ws.sub(r"\1", string)

    return VCSTranslation(
        key=key,
        context=key,
        order=order,
        string=string,
        source_string=string,
        comments=entry.comment.split("\n") if entry.comment else None,
    )
