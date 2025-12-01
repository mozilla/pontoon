"""
Parsing resource files.
"""

from dataclasses import dataclass
from os.path import splitext
from re import Match, compile
from typing import Iterator

from fluent.syntax import FluentSerializer
from moz.l10n.formats import Format, detect_format, l10n_extensions
from moz.l10n.formats.fluent import fluent_astify_entry
from moz.l10n.message import message_to_json, serialize_message
from moz.l10n.model import (
    CatchallKey,
    Entry,
    Expression,
    Id as L10nId,
    Message,
    PatternMessage,
    Resource as MozL10nResource,
    SelectMessage,
    VariableRef,
)

from pontoon.base.models import Entity


@dataclass
class VCSTranslation:
    """
    A single translation of a source string into another language.
    """

    key: tuple[str, ...]
    string: str
    fuzzy: bool = False


def are_compatible_files(file_a, file_b):
    """
    Return True if the given file names correspond to the same file format.
    Note that some formats (e.g. Gettext, XLIFF) use multiple file name patterns.
    """
    _, ext_a = splitext(file_a)
    _, ext_b = splitext(file_b)
    if ext_a in l10n_extensions and ext_b in l10n_extensions:
        if ext_a == ext_b:
            return True
        fmt_a = detect_format(file_a)
        fmt_b = detect_format(file_b)
        return fmt_a is not None and fmt_a == fmt_b
    return False


_fluent_serializer = FluentSerializer()
_prop_esc_u = compile(r"(?<!\\)\\u(?!0000)[0-9A-Fa-f]{4}")
_prop_esc_ws = compile(r"(?<!\\)\\([^\S\n])")


def _unicode_unescape(m: Match[str]):
    return m[0].encode("utf-8").decode("unicode_escape")


def _as_string(format: Format | None, entry: Entry[Message]) -> str:
    match format:
        case Format.fluent:
            fluent_entry = fluent_astify_entry(entry, lambda _: "")
            return _fluent_serializer.serialize_entry(fluent_entry)
        case Format.android | Format.gettext | Format.webext | Format.xliff:
            return serialize_message(Format.mf2, entry.value)
        case Format.properties:
            string = serialize_message(Format.properties, entry.value)
            string = _prop_esc_u.sub(_unicode_unescape, string)
            string = _prop_esc_ws.sub(r"\1", string)
            return string
        case _:
            return serialize_message(format, entry.value)


def as_vcs_translations(res: MozL10nResource[Message]) -> Iterator[VCSTranslation]:
    for section in res.sections:
        if res.format == Format.android and section.id:
            continue
        for entry in section.entries:
            if isinstance(entry, Entry) and not (
                res.format in {Format.gettext, Format.xliff} and entry.value.is_empty()
            ):
                fuzzy = (
                    any(m.key == "flag" and m.value == "fuzzy" for m in entry.meta)
                    if res.format == Format.gettext
                    else False
                )
                yield VCSTranslation(
                    key=section.id + entry.id,
                    string=_as_string(res.format, entry),
                    fuzzy=fuzzy,
                )


def as_entity(
    format: Format | None,
    section_id: L10nId,
    entry: Entry[Message],
    **kwargs,
) -> Entity:
    """At least `order`, `resource`, and `section` should be set as `kwargs`."""
    if format == Format.gettext:
        source_str = entry.id[0]
        plural_str = entry.get_meta("plural")
        source_msg = (
            PatternMessage([source_str])
            if plural_str is None
            else SelectMessage(
                declarations={"n": Expression(VariableRef("n"), "number")},
                selectors=(VariableRef("n"),),
                variants={
                    ("one",): [source_str],
                    (CatchallKey("other"),): [plural_str],
                },
            )
        )

        return Entity(
            key=list(entry.id),
            value=message_to_json(source_msg),
            string=serialize_message(Format.mf2, source_msg),
            comment=entry.comment,
            meta=[[m.key, m.value] for m in entry.meta],
            **kwargs,
        )

    return Entity(
        key=list(section_id + entry.id),
        value=message_to_json(entry.value),
        properties=(
            {name: message_to_json(value) for name, value in entry.properties.items()}
            if entry.properties
            else None
        ),
        string=_as_string(format, entry),
        comment=entry.comment,
        meta=[[m.key, m.value] for m in entry.meta],
        **kwargs,
    )
