import re
from copy import deepcopy
from typing import Callable, Optional, Union, cast

from fluent.syntax import ast as FTL
from fluent.syntax.serializer import serialize_expression
from fluent.syntax.visitor import Transformer

from pontoon.base.fluent import is_plural_expression
from pontoon.base.models import Locale
from .plural_examples import find_plural_example


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


class NotranslateWrapper(Transformer):
    """
    Replaces all placeables with a `<span id="pt-#" translate="no">...</span>`
    text element where the `#` identifies an entry in `replacements`,
    and the `...` is a sanitized representation of the placeable's serialization.
    If a variable `pluralSelector` is given, references to that variable
    will use a numerical value appropriate for each variant.
    """

    def __init__(
        self,
        locale: Locale,
        replacements: list[str],
        pluralSelector: Optional[FTL.InlineExpression] = None,
    ):
        self.locale = locale
        self.replacements = replacements
        self.pluralVar = (
            pluralSelector.id.name
            if isinstance(pluralSelector, FTL.VariableReference)
            else None
        )
        self.pluralKey: Union[float, int, str, None] = None

    def visit_Variant(self, node: FTL.Variant):
        if self.pluralVar is not None:
            self.pluralKey = (
                node.key.parse()["value"]
                if isinstance(node.key, FTL.NumberLiteral)
                else node.key.name
            )
        return self.generic_visit(node)

    def visit_Placeable(self, node: FTL.Placeable):
        source = serialize_expression(node)
        idx = len(self.replacements)
        self.replacements.append(source)
        clean: str
        if (
            self.pluralKey is not None
            and isinstance(node.expression, FTL.VariableReference)
            and node.expression.id.name == self.pluralVar
        ):
            clean = (
                find_plural_example(self.locale, self.pluralKey)
                if isinstance(self.pluralKey, str)
                else str(self.pluralKey)
            )
        else:
            clean = re.sub(r"[<>{}\n]", "", source).strip()
        return FTL.TextElement(f'<span id="pt-{idx}" translate="no">{clean}</span>')


class PreparePretranslation(Transformer):
    """
    Flattens the given Pattern, uplifting selectors to the highest possible level and
    duplicating shared parts in the variants. All other Placeables are serialised as
    TextElements.
    """

    def __init__(self, locale: Locale):
        self.locale = locale
        self.replacements: list[str] = []

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
            NotranslateWrapper(
                self.locale, self.replacements, node.selector
            ).generic_visit(node)
        return self.generic_visit(node)


class ApplyPretranslation(Transformer):
    """
    During `visit()`, calls `callback(raw, wrapped, locale) -> (translation, service)` for each pattern.
    """

    def __init__(
        self,
        locale: Locale,
        entry: FTL.EntryType,
        callback: Callable[[str, str, str], tuple[Optional[str], str]],
    ):
        prep = PreparePretranslation(locale)
        prep.visit(entry)
        self.callback = callback
        self.locale = locale
        self.replacements = prep.replacements
        self.notranslate = NotranslateWrapper(locale, self.replacements)
        self.services: list[str] = []

    def applyReplacements(self, translation: str):
        return re.sub(
            r'<span id="pt-(\d+)" translate="no">[^<>]*</span>',
            lambda m: self.replacements[int(m.group(1))],
            translation,
        )

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
                text = self.notranslate.visit_Placeable(el)
                source += text.value
        if not has_selects and source != "":
            # Machine translation treats each line as a separate sentence,
            # hence we replace newline characters with spaces.
            source = source.replace("\n", " ")

            raw = self.applyReplacements(source)
            translation, service = self.callback(raw, source, self.locale)
            if translation is None:
                raise ValueError(
                    f"Pretranslation for `{source}` to {self.locale.code} not available."
                )
            node.elements = [FTL.TextElement(self.applyReplacements(translation))]
            self.services.append(service)
        return node
