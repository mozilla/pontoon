from collections.abc import Iterator
from typing import TypedDict

from moz.l10n.formats.fluent import fluent_parse_entry
from moz.l10n.model import (
    CatchallKey,
    Entry,
    Expression,
    Message,
    Pattern,
    PatternMessage,
    SelectMessage,
)


def _parse_fluent_entry(source: str) -> Entry[Message] | None:
    """Parse a Fluent entry; returns None if the source is invalid FTL."""
    try:
        return fluent_parse_entry(source, with_linepos=False)
    except ValueError:
        return None


def _entry_messages(entry: Entry[Message]) -> Iterator[Message]:
    """Iterate over the entry's value message and its property messages."""
    if isinstance(entry.value, (PatternMessage, SelectMessage)):
        yield entry.value
    yield from entry.properties.values()


def get_references(entry: Entry[Message]) -> set[str]:
    """Collect the keys of the messages/terms referenced by a Fluent entry, e.g.
    `-brand-name` in `msg = This is { -brand-name }`.
    """
    names: set[str] = set()

    def from_expression(expr: Expression) -> None:
        # Remember message/term references
        if expr.function == "message" and isinstance(expr.arg, str):
            names.add(expr.arg)

    def from_pattern(pattern: Pattern) -> None:
        for part in pattern:
            if isinstance(part, Expression):
                from_expression(part)

    def from_message(msg: Message) -> None:
        for expr in msg.declarations.values():
            from_expression(expr)
        if isinstance(msg, PatternMessage):
            from_pattern(msg.pattern)
        elif isinstance(msg, SelectMessage):
            for pattern in msg.variants.values():
                from_pattern(pattern)

    for msg in _entry_messages(entry):
        from_message(msg)

    return names


class SelectorField(TypedDict):
    """A selector from a Fluent entry, together with its variant keys."""

    name: str
    values: list[str]


def get_selector_variants(entry: Entry[Message]) -> list[SelectorField]:
    """Extract the selector fields and their variants from a Fluent entry's
    value and attributes.

    Note default variants always come last, which is the same way as provided by
    moz.l10n.fluent.
    """
    fields: dict[str, list[str]] = {}
    for msg in _entry_messages(entry):
        # Only selectors contain variants, so we skip any other message type.
        if not isinstance(msg, SelectMessage):
            continue

        for idx, selector in enumerate(msg.selectors):
            values = fields.setdefault(selector.name, [])
            for keys in msg.variants:
                key = keys[idx]
                value = key.value if isinstance(key, CatchallKey) else key
                if value and value not in values:
                    values.append(value)

    return [{"name": name, "values": values} for name, values in fields.items()]
