import re
from copy import deepcopy
from typing import Callable, Dict, List, Optional, Tuple, Union, cast

from fluent.syntax import ast as FTL
from fluent.syntax.serializer import serialize_expression
from fluent.syntax.visitor import Transformer

from pontoon.base.fluent import is_plural_expression
from pontoon.base.models import Locale


def flatten_pattern_elements(pattern: FTL.Pattern, replacements: List[str]):
    """
    Serialize all Placeables other than selects as TextElements.
    """
    flat_elements: List[Union[FTL.TextElement, FTL.Placeable]] = []
    text_fragment: str = ""
    prev_select: Optional[FTL.SelectExpression] = None

    for element in pattern.elements:
        if isinstance(element, FTL.Placeable) and isinstance(
            element.expression, FTL.SelectExpression
        ):
            # In a message with multiple SelectExpressions separated by some
            # whitespace, keep that whitespace out of select variants.
            if re.search("^\\s+$", text_fragment):
                flat_elements.append(FTL.TextElement(text_fragment))
                text_fragment = ""

            # Flatten SelectExpression variant elements
            for variant in element.expression.variants:
                flatten_pattern_elements(variant.value, replacements)

                # If there is preceding text, include that for all variants
                if text_fragment:
                    elements = variant.value.elements
                    if elements and isinstance(elements[0], FTL.TextElement):
                        first = elements[0]
                        first.value = text_fragment + first.value
                    else:
                        elements.insert(0, FTL.TextElement(text_fragment))

            if text_fragment:
                text_fragment = ""

            flat_elements.append(element)
            prev_select = element.expression

        else:
            str_value: str
            if isinstance(element, FTL.TextElement):
                str_value = element.value
            else:
                src = serialize_expression(element)
                idx = len(replacements)
                replacements.append(src)
                clean = re.sub(r"[<>\n]", "", src)
                str_value = f'<span id="pt-{idx}" translate="no">{clean}</span>'

            if text_fragment:
                str_value = text_fragment + str_value
                text_fragment = ""

            if prev_select:
                # Keep trailing whitespace out of variant values
                ws_end = re.match("\\s+$", str_value)
                if ws_end:
                    str_value = str_value[0 : ws_end.index]
                    text_fragment = ws_end[0]

                # If there is a preceding SelectExpression, append to each of its variants
                for variant in prev_select.variants:
                    elements = variant.value.elements
                    if elements and isinstance(elements[-1], FTL.TextElement):
                        last = elements[-1]
                        last.value += str_value
                    else:
                        elements.append(FTL.TextElement(str_value))
            else:
                # ... otherwise, append to a temporary string
                text_fragment += str_value

    # Merge any remaining collected text into a TextElement
    if text_fragment or len(flat_elements) == 0:
        flat_elements.append(FTL.TextElement(text_fragment))

    pattern.elements = flat_elements


def create_locale_plural_variants(node: FTL.SelectExpression, locale: Locale):
    if not is_plural_expression(node):
        return

    variants: List[FTL.Variant] = []
    source_plurals: Dict[str, FTL.Variant] = {}
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


class PretranslationTransformer(Transformer):
    """
    Flattens the given Pattern, uplifting selectors to the highest possible level and
    duplicating shared parts in the variants. All other Placeables are serialised as
    TextElements.
    """

    def __init__(
        self,
        locale: Locale,
        callback: Callable[[str, str, str], Tuple[Optional[str], str]],
    ):
        self.locale = locale
        self.callback = callback
        self.replacements: List[str] = []
        self.services: List[str] = []

    def applyReplacements(self, translation: str):
        return re.sub(
            r'<span id="pt-(\d+)" translate="no">[^<>]*</span>',
            lambda m: self.replacements[int(m.group(1))],
            translation,
        )

    def visit_Attribute(self, node: FTL.Attribute):
        flatten_pattern_elements(node.value, self.replacements)
        return self.generic_visit(node)

    def visit_Message(self, node: FTL.Message):
        if node.value:
            flatten_pattern_elements(node.value, self.replacements)
        return self.generic_visit(node)

    def visit_SelectExpression(self, node: FTL.SelectExpression):
        create_locale_plural_variants(node, self.locale)
        return self.generic_visit(node)

    def visit_TextElement(self, node: FTL.TextElement):
        raw = self.applyReplacements(node.value)
        translation, service = self.callback(raw, node.value, self.locale)

        if translation is None:
            raise ValueError(
                f"Pretranslation for `{node.value}` to {self.locale.code} not available."
            )

        node.value = self.applyReplacements(translation)
        self.services.append(service)
        return node
