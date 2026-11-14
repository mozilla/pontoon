"""Pairing an entity's source leaves with the leaves of a composed translation.

A composed suggestion is assembled leaf by leaf, so refining it means refining
each leaf against the English that leaf came from.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass

from moz.l10n.formats import Format
from moz.l10n.model import (
    CatchallKey,
    Message,
    Pattern,
    PatternMessage,
    SelectMessage,
)

from pontoon.pretranslation.pretranslate import pattern_as_context


@dataclass
class Leaf:
    """`target` is live, so refining a leaf is an assignment to `target[:]`."""

    id: str
    source: Pattern
    target: Pattern


def _variant_key_label(keys: tuple[str | CatchallKey, ...]) -> str:
    return ", ".join(
        key.value or "*" if isinstance(key, CatchallKey) else key for key in keys
    )


def _source_variant(
    source: SelectMessage, keys: tuple[str | CatchallKey, ...]
) -> Pattern:
    """`Pretranslation.message()` fans the source's catchall out to every plural
    category the target locale declares, so a target key often has no counterpart
    in the source: `many` in Polish comes from en-US's `other`.
    """
    exact = source.variants.get(keys)
    if exact is not None:
        return exact

    for src_keys, pattern in source.variants.items():
        if len(src_keys) == len(keys) and all(
            isinstance(src_key, CatchallKey) or src_key == key
            for src_key, key in zip(src_keys, keys)
        ):
            return pattern

    return list(source.variants.values())[-1]


def _message_leaves(leaf_id: str, source: Message, target: Message) -> Iterator[Leaf]:
    if isinstance(target, PatternMessage):
        source_pattern = (
            source.pattern
            if isinstance(source, PatternMessage)
            else list(source.variants.values())[-1]
        )
        yield Leaf(leaf_id, source_pattern, target.pattern)
    else:
        for keys, pattern in target.variants.items():
            source_pattern = (
                source.pattern
                if isinstance(source, PatternMessage)
                else _source_variant(source, keys)
            )
            yield Leaf(
                f"{leaf_id}[{_variant_key_label(keys)}]", source_pattern, pattern
            )


def is_accesskey(key: str) -> bool:
    """Accesskeys are derived from their label, so they are never refined directly."""
    return key.lower().endswith("accesskey")


def iter_leaves(
    source_value: Message,
    source_properties: dict[str, Message],
    target_value: Message,
    target_properties: dict[str, Message],
) -> Iterator[Leaf]:
    """Yield every refinable leaf of a composed translation, paired with its source.

    Properties absent from the source are skipped: without English to refine
    against, the LLM would be guessing.
    """
    if target_value is not None and source_value is not None:
        yield from _message_leaves("value", source_value, target_value)

    for key, target in target_properties.items():
        source = source_properties.get(key)
        if source is None or is_accesskey(key):
            continue
        yield from _message_leaves(f".{key}", source, target)


def has_translatable_text(pattern: Pattern) -> bool:
    """A pattern of nothing but placeholders has no words to refine."""
    return any(isinstance(el, str) and el.strip() for el in pattern)


def placeables_survived(
    refined: Pattern, current: Pattern, format: Format | None
) -> bool:
    """Whether a refined leaf still carries the placeables it was given.

    Parsing says the reply is well-formed, not that it kept the variables:
    `Zdravo { $name }` refined to `Pozdravljeni` parses cleanly and has silently
    lost `$name`. Order is free, because languages reorder.

    Placeables are compared as the text the format writes them as, which draws
    the line in the right place on its own: the function in `{ NUMBER($n) }`,
    its options, and a term's arguments all have to match, while the `number`
    annotation Fluent infers for a plural selector and never writes does not.
    """

    def placeables(pattern: Pattern) -> Counter:
        return Counter(
            pattern_as_context([el], format)
            for el in pattern
            if not isinstance(el, str)
        )

    return placeables(refined) == placeables(current)
