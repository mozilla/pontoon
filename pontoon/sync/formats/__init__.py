"""
Parsing resource files.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from os.path import splitext

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


def fluent_nested_same_selector_keys(source: str) -> set[str]:
    """
    Return the names of Fluent entries with a select expression nested inside
    another select using the same selector.

    moz.l10n (<= 0.14.2) collapses such nesting when parsing, dropping the
    outer text of the inner variants (mozilla/moz-l10n#211, pontoon#4183).
    Callers use this to avoid persisting the corrupted flattening until the
    library is fixed. Never raises; returns an empty set when parsing fails.
    """
    try:
        from fluent.syntax import FluentParser, ast as fluent_ast
    except ImportError:
        return set()
    try:
        res = FluentParser().parse(source)
    except Exception:
        return set()

    def selector_key(selector) -> tuple:
        if isinstance(selector, fluent_ast.VariableReference):
            return ("var", selector.id.name)
        if isinstance(selector, fluent_ast.TermReference):
            return ("term", selector.id.name)
        if isinstance(selector, fluent_ast.MessageReference):
            return ("msg", selector.id.name)
        return (type(selector).__name__,)

    def has_nested_same_selector(node, ancestors: tuple = ()) -> bool:
        if isinstance(node, fluent_ast.SelectExpression):
            key = selector_key(node.selector)
            if key in ancestors:
                return True
            ancestors = ancestors + (key,)
            return any(
                has_nested_same_selector(v.value, ancestors) for v in node.variants
            )
        if isinstance(node, fluent_ast.Pattern):
            return any(has_nested_same_selector(el, ancestors) for el in node.elements)
        if isinstance(node, fluent_ast.Placeable):
            return has_nested_same_selector(node.expression, ancestors)
        return False

    found: set[str] = set()
    for entry in res.body:
        if not isinstance(entry, (fluent_ast.Message, fluent_ast.Term)):
            continue
        try:
            nested = entry.value is not None and has_nested_same_selector(entry.value)
            if not nested:
                for attr in entry.attributes or []:
                    if has_nested_same_selector(attr.value):
                        nested = True
                        break
            if nested:
                # fluent.syntax Term ids omit the leading "-", which Pontoon
                # (and moz.l10n) entry ids include.
                name = entry.id.name
                if isinstance(entry, fluent_ast.Term):
                    name = "-" + name
                found.add(name)
        except Exception:
            continue
    return found


@dataclass
class RepoTranslation:
    """
    A single translation of a source string into another language.
    """

    key: tuple[str, ...]
    string: str
    value: Message
    properties: dict[str, Message] | None = None
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


def as_string(
    format: Format | None, entry: Entry[Message], *, fluent_escape_syntax: bool = True
) -> str:
    match format:
        case Format.fluent:
            fluent_entry = fluent_astify_entry(
                entry, comment_str=lambda _: "", escape_syntax=fluent_escape_syntax
            )
            return FluentSerializer().serialize_entry(fluent_entry)
        case Format.android | Format.gettext | Format.webext | Format.xliff:
            return serialize_message(Format.mf2, entry.value)
        case _:
            return serialize_message(format, entry.value)


def as_repo_translations(res: MozL10nResource[Message]) -> Iterator[RepoTranslation]:
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
                yield RepoTranslation(
                    key=section.id + entry.id,
                    string=as_string(res.format, entry),
                    value=entry.value,
                    properties=entry.properties,
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
        string=as_string(format, entry),
        comment=entry.comment,
        meta=[[m.key, m.value] for m in entry.meta],
        **kwargs,
    )
