import re

from copy import deepcopy
from typing import Callable, Optional, cast

from fluent.syntax import ast as FTL
from fluent.syntax.serializer import serialize_expression
from fluent.syntax.visitor import Transformer

from pontoon.base.fluent import is_plural_expression
from pontoon.base.models import Locale


def flatten_select_expressions(pattern: FTL.Pattern):
    """
    If the pattern contains any select expressions,
    flatten it to only contain select expressions.
    Leading and trailing elements are copied into each variant,
    and any single leading or trailing spaces are lifted out of the select expressions.
    """

    def isSelExp(el: FTL.PatternElement):
        return isinstance(el, FTL.Placeable) and isinstance(
            el.expression, FTL.SelectExpression
        )

    def patternStartsWithSpace(pat: list[FTL.PatternElement]):
        return isinstance(pat[0], FTL.TextElement) and pat[0].value.startswith(" ")

    def patternEndsWithSpace(pat: list[FTL.PatternElement]):
        return isinstance(pat[-1], FTL.TextElement) and pat[-1].value.endswith(" ")

    prev = -1
    select = None
    for idx, placeable in filter(lambda x: isSelExp(x[1]), enumerate(pattern.elements)):
        before = pattern.elements[prev + 1 : idx]
        if before:
            select = cast(FTL.SelectExpression, placeable.expression)
            for variant in select.variants:
                variant.value.elements[0:0] = deepcopy(before)
        prev = idx
    if select:
        after = pattern.elements[prev + 1 :]
        if after:
            for variant in select.variants:
                variant.value.elements += deepcopy(after)

        res: list[FTL.PatternElement] = []
        for placeable in filter(isSelExp, pattern.elements):
            patterns = tuple(
                map(lambda var: var.value.elements, placeable.expression.variants)
            )

            # Collect leading spaces
            if all(map(patternStartsWithSpace, patterns)):
                res.append(FTL.Placeable(FTL.StringLiteral(" ")))
                for pat in patterns:
                    pat[0].value = pat[0].value[1:]

            res.append(placeable)

            # Collect trailing spaces
            if all(map(patternEndsWithSpace, patterns)):
                res.append(FTL.Placeable(FTL.StringLiteral(" ")))
                for pat in patterns:
                    pat[-1].value = pat[-1].value[:-1]
        pattern.elements = res


def create_locale_plural_variants(node: FTL.SelectExpression, locale: Locale):
    variants: list[FTL.Variant] = []
    source_plurals: dict[str, FTL.Variant] = {}
    default = cast(FTL.Variant, None)

    for variant in node.variants:
        key = variant.key
        if isinstance(key, FTL.NumberLiteral):
            variants.append(variant)
        else:
            source_plurals[key.name] = variant
        if variant.default:
            default = variant

    for plural in locale.cldr_plurals_list():
        if plural in source_plurals.keys():
            variant = source_plurals[plural]
        else:
            variant = deepcopy(default)
            variant.key.name = plural
        variant.default = False
        variants.append(variant)

    variants[-1].default = True

    node.variants = variants


def extract_accesskey_candidates(message: FTL.Message, label: str, variant_name=None):
    def get_source(names):
        for attribute in message.attributes:
            if attribute.id.name in names:
                element = attribute.value.elements[0]

                if isinstance(element, FTL.TextElement):
                    return element.value
                elif isinstance(element.expression, FTL.SelectExpression):
                    variants = element.expression.variants
                    variant = next(
                        (v for v in variants if v.key.name == variant_name), variants[0]
                    )
                    variant_element = variant.value.elements[0]

                    if isinstance(variant_element, FTL.TextElement):
                        return variant_element.value

        return None

    prefix_end = label.index("accesskey")
    prefix = label[0:prefix_end]

    # Generate access key candidates:
    if prefix:
        # From a prefixed "label" attribute
        name = f"{prefix}label"
        source = get_source([name])
    else:
        # From a pre-defined list of attribute names
        source = get_source(["label", "value", "aria-label"])
        # From a message value
        if not source and message.value:
            source = message.value.elements[0].value

    if not source:
        return []

    # Exclude placeables (message is flat). See bug 1447103 for details.
    keys = re.sub(r"(?s){.*?}|[\W_]", "", source)

    # Extract unique candidates
    return list(dict.fromkeys(keys))


class PreparePretranslation(Transformer):
    """
    Flattens the given Pattern, uplifting selectors to the highest possible level and
    duplicating shared parts in the variants. Transforms plural variants to match the
    locale.
    """

    def __init__(self, locale: Locale):
        self.locale = locale

    def visit_Attribute(self, node: FTL.Attribute):
        flatten_select_expressions(node.value)
        return self.generic_visit(node)

    def visit_Message(self, node: FTL.Message):
        if node.value:
            flatten_select_expressions(node.value)
        return self.generic_visit(node)

    def visit_SelectExpression(self, node: FTL.SelectExpression):
        if is_plural_expression(node):
            create_locale_plural_variants(node, self.locale)
        return self.generic_visit(node)


class ApplyPretranslation(Transformer):
    """
    During `visit()`, calls `callback(source, locale) -> (translation, service)` for each pattern.
    """

    def __init__(
        self,
        locale: Locale,
        entry: FTL.EntryType,
        callback: Callable[[str, str], tuple[Optional[str], str]],
        preserve_placeables: bool = None,
    ):
        prep = PreparePretranslation(locale)
        prep.visit(entry)
        self.preserve_placeables = preserve_placeables
        self.callback = callback
        self.entry = entry
        self.locale = locale
        self.services: list[str] = []

    def visit_Attribute(self, node: FTL.Pattern):
        name = node.id.name

        def set_accesskey(element, variant_name=None):
            if isinstance(element, FTL.TextElement) and len(element.value) <= 1:
                candidates = extract_accesskey_candidates(
                    self.entry, name, variant_name
                )
                if candidates:
                    element.value = candidates[0]
                    return True

        if name.endswith("accesskey"):
            if self.locale.accesskey_localization:
                element = node.value.elements[0]

                if set_accesskey(element):
                    return node
                elif isinstance(element, FTL.Placeable) and isinstance(
                    element.expression, FTL.SelectExpression
                ):
                    variants = element.expression.variants
                    processed_variants = 0
                    for variant in variants:
                        variant_element = variant.value.elements[0]
                        if set_accesskey(variant_element, variant.key.name):
                            processed_variants += 1
                    if processed_variants == len(variants):
                        return node

            else:
                return node

        return self.generic_visit(node)

    def visit_Pattern(self, node: FTL.Pattern):
        has_selects = False
        source = ""
        for el in node.elements:
            if isinstance(el, FTL.TextElement):
                source += el.value
            elif isinstance(el.expression, FTL.SelectExpression):
                self.generic_visit(el.expression)
                has_selects = True
            else:
                source += serialize_expression(el)
        if not has_selects and source != "":
            # Machine translation treats each line as a separate sentence,
            # hence we replace newline characters with spaces.
            source = source.replace("\n", " ")

            translation, service = self.callback(
                source, self.locale, self.preserve_placeables
            )
            if translation is None:
                raise ValueError(
                    f"Pretranslation for `{source}` to {self.locale.code} not available."
                )
            node.elements = [FTL.TextElement(translation)]
            self.services.append(service)
        return node
