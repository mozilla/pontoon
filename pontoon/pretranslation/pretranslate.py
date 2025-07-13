from copy import deepcopy
from re import compile
from typing import Literal

from fluent.syntax import FluentSerializer, ast as FTL
from fluent.syntax.serializer import serialize_expression
from moz.l10n.formats import Format
from moz.l10n.formats.fluent import (
    fluent_astify_entry,
    fluent_astify_message,
    fluent_parse_entry,
)
from moz.l10n.message import parse_message, serialize_message
from moz.l10n.model import (
    CatchallKey,
    Entry,
    Expression,
    Markup,
    Message,
    Pattern,
    PatternMessage,
)

from pontoon.base.models import Entity, Locale, Resource, TranslationMemoryEntry
from pontoon.machinery.utils import get_google_translate_data


pt_placeholder = compile(r"{ *\$(\d+) *}")


def get_pretranslation(
    entity: Entity, locale: Locale, preserve_placeables: bool = False
) -> tuple[str, Literal["gt", "tm"]]:
    """
    Get pretranslations for the entity-locale pair using internal translation memory and
    Google's machine translation.

    For entities with multiple variants and/or Fluent attributes,
    sets the most frequent pretranslation author as the author of the entire pretranslation.

    :returns: A tuple consisting of:
        - a pretranslation of the entity
        - a pretranslation service identifier, either "gt" or "tm"
    """

    pt = Pretranslation(entity, locale, preserve_placeables)
    if entity.resource.format == Resource.Format.FLUENT:
        entry = fluent_parse_entry(entity.string, with_linepos=False)
        if entry.value:
            pt.message(entry.value)
        accesskeys: list[tuple[str, Message]] = []
        for key, prop in entry.properties.items():
            if key.endswith("accesskey"):
                accesskeys.append((key, prop))
            else:
                pt.message(prop)
        for key, prop in accesskeys:
            set_accesskey(entry, key, prop)
        pt_res = FluentSerializer().serialize_entry(fluent_astify_entry(entry))
    else:
        if entity.resource.format == Resource.Format.GETTEXT:
            format = Format.mf2
            msg = parse_message(format, entity.string)
        else:
            format = None
            msg = PatternMessage([entity.string])
        pt.message(msg)
        pt_res = serialize_message(format, msg)

    pt_service = max(set(pt.services), key=pt.services.count) if pt.services else "tm"
    return (pt_res, pt_service)


class Pretranslation:
    format: Format | None
    locale: Locale
    preserve_placeables: bool
    services: list[Literal["gt", "tm"]]
    source: str

    def __init__(self, entity: Entity, locale: Locale, preserve_placeables: bool):
        match entity.resource.format:
            case Resource.Format.FLUENT:
                self.format = Format.fluent
            case Resource.Format.GETTEXT:
                self.format = Format.mf2
            case _:
                self.format = None
        self.source = entity.string
        self.locale = locale
        self.preserve_placeables = preserve_placeables
        self.services = []

    def message(self, msg: Message) -> None:
        """Modifies `msg`."""
        if isinstance(msg, PatternMessage):
            msg.pattern = self.pattern(msg.pattern)
        else:
            # catchall category is always last, and is always included
            plurals = self.locale.cldr_plurals_list()[:-1]

            # Plural selectors need special attention
            plural_selectors = [
                idx
                for idx, sel in enumerate(msg.selector_expressions())
                if sel.function in ("integer", "number")
            ]

            # Do not translate plural "one" variants if not used in the target locale
            has_pc_one = "one" in plurals
            rm_keys = []
            for keys, pattern in msg.variants.items():
                if not has_pc_one and any(
                    keys[idx] == "one" for idx in plural_selectors
                ):
                    rm_keys.append(keys)
                else:
                    pattern[:] = self.pattern(pattern)
            for keys in rm_keys:
                del msg.variants[keys]

            # Copy catchall patterns for the locale's other plural categories
            if plurals:
                for idx in plural_selectors:
                    tgt_variants = {}
                    for keys, pattern in msg.variants.items():
                        key = keys[idx]
                        if isinstance(key, CatchallKey):
                            for pc in plurals:
                                pc_keys = keys[:idx] + (pc,) + keys[idx + 1 :]
                                if pc_keys not in msg.variants:
                                    tgt_variants[pc_keys] = deepcopy(pattern)
                        tgt_variants[keys] = pattern
                    msg.variants = tgt_variants

    def pattern(self, pattern: Pattern) -> Pattern:
        # First try to get a 100% match from Translation Memory
        tm_source = (
            "".join(
                el.value
                if isinstance(el, FTL.TextElement)
                else serialize_expression(el)
                for el in fluent_astify_message(PatternMessage(pattern)).elements
            )
            if self.format == Format.fluent
            else self.source
        )
        if not tm_source or tm_source.isspace():
            return pattern
        tm_q100 = list(
            TranslationMemoryEntry.objects.filter(
                locale=self.locale, source=tm_source
            ).values_list("target", flat=True)
        )
        if tm_q100:
            tm_best = max(set(tm_q100), key=tm_q100.count)
            self.services.append("tm")
            if self.format == Format.fluent:
                te = fluent_parse_entry(f"key = {tm_best}\n")
                assert isinstance(te.value, PatternMessage)
                return te.value.pattern
            else:
                return [tm_best]

        placeholders: list[Expression | Markup] = []
        gt_source = ""
        has_text = False
        for el in pattern:
            if isinstance(el, str):
                if el and not el.isspace():
                    has_text = True
                # Machine translation treats each line as a separate sentence,
                # hence we replace newline characters with spaces.
                gt_source += el.replace("\n", " ")
            else:
                idx = len(placeholders)
                placeholders.append(el)
                gt_source += "{$" + str(idx) + "}"
        if not has_text:
            return pattern

        if self.locale.google_translate_code:
            # Try to fetch from Google Translate
            gt_response = get_google_translate_data(
                text=gt_source,
                locale=self.locale,
                preserve_placeables=self.preserve_placeables,
            )
            if gt_response["status"]:
                self.services.append("gt")
                return [
                    el
                    if idx % 2 == 0
                    else (
                        placeholders[int(el)]
                        if int(el) < len(placeholders)
                        else "{$" + el + "}"
                    )
                    for idx, el in enumerate(
                        pt_placeholder.split(gt_response["translation"])
                    )
                    if el != ""
                ]

        raise ValueError(
            f"Pretranslation for `{self.source}` to {self.locale.code} not available."
        )


def set_accesskey(entry: Entry[Message], ak_name: str, ak_msg: Message):
    """Modifies `ak_msg`."""

    if ak_name == "accesskey":
        label = next(
            (
                value
                for key, value in entry.properties.items()
                if key in {"label", "value", "aria-label"}
            ),
            entry.value,
        )
    else:
        label = entry.properties.get(ak_name.replace("accesskey", "label"), None)
        if label is None:
            return

    def get_first_char(pattern: Pattern):
        return next(
            (
                ch
                for part in pattern
                if isinstance(part, str) and (ch := part.lstrip()[:1])
            ),
            None,
        )

    if isinstance(ak_msg, PatternMessage):
        if len(ak_msg.pattern) == 1 and isinstance(ak_msg.pattern[0], str):
            if isinstance(label, PatternMessage):
                first_char = get_first_char(label.pattern)
            else:
                catchall = tuple(CatchallKey() for _ in label.selectors)
                first_char = get_first_char(label.variants[catchall])
            if first_char:
                ak_msg.pattern = [first_char]
    elif isinstance(label, PatternMessage):
        first_char = get_first_char(label.pattern)
        if first_char:
            for pattern in ak_msg.variants.values():
                pattern[:] = [first_char]
    elif ak_msg.selector_expressions() == label.selector_expressions() and set(
        ak_msg.variants
    ) == set(label.variants):
        for keys, pattern in ak_msg.variants.items():
            first_char = get_first_char(label.variants[keys])
            if first_char:
                pattern[:] = [first_char]
