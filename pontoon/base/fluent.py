import copy
import re

from fluent.syntax import ast, FluentParser, visitor
from fluent.syntax.serializer import serialize_expression


parser = FluentParser()


class FlatTransformer(visitor.Transformer):
    """
    Flattens the given Pattern, uplifting selectors to the highest possible level and
    duplicating shared parts in the variants. All other Placeables are serialised as
    TextElements.

    Empty String Literals `{ "" }` are transformed into empty TextElements.
    """

    def visit_Attribute(self, node):
        flatten_pattern_elements(node.value)
        return self.generic_visit(node)

    def visit_Message(self, node):
        if node.value:
            flatten_pattern_elements(node.value)
        return self.generic_visit(node)

    def visit_TextElement(self, node):
        node.value = re.sub(r'{ "" }', "", node.value)
        return node


def flatten_pattern_elements(pattern):
    """
    Serialize all Placeables other than selects as TextElements.

    Should only be called externally with the value of a Message or an Attribute.
    """
    flat_elements = []
    text_fragment = ""
    prev_select = None

    for element in pattern.elements:
        if isinstance(element, ast.Placeable) and isinstance(
            element.expression, ast.SelectExpression
        ):
            # In a message with multiple SelectExpressions separated by some
            # whitespace, keep that whitespace out of select variants.
            if re.search("^\\s+$", text_fragment):
                flat_elements.append(ast.TextElement(text_fragment))
                text_fragment = ""

            # Flatten SelectExpression variant elements
            for variant in element.expression.variants:
                flatten_pattern_elements(variant.value)

                # If there is preceding text, include that for all variants
                if text_fragment:
                    elements = variant.value.elements
                    if elements and isinstance(elements[0], ast.TextElement):
                        first = elements[0]
                        first.value = text_fragment + first.value
                    else:
                        elements.insert(0, ast.TextElement(text_fragment))

            if text_fragment:
                text_fragment = ""

            flat_elements.append(element)
            prev_select = element.expression

        else:
            str_value = (
                element.value
                if isinstance(element, ast.TextElement)
                else serialize_expression(element)
            )
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
                    if elements and isinstance(elements[-1], ast.TextElement):
                        last = elements[-1]
                        last.value += str_value
                    else:
                        elements.append(ast.TextElement(str_value))
            else:
                # ... otherwise, append to a temporary string
                text_fragment += str_value

    # Merge any remaining collected text into a TextElement
    if text_fragment or len(flat_elements) == 0:
        flat_elements.append(ast.TextElement(text_fragment))

    pattern.elements = flat_elements


def get_default_variant(variants):
    """Return default variant from the list of variants."""
    for variant in variants:
        if variant.default:
            return variant


def serialize_value(value):
    """Serialize AST value into a simple string.

    Presumes that the default variant is the most appropriate to use as a generic
    representation of the message
    """
    response = ""

    for element in value.elements:
        if isinstance(element, ast.TextElement):
            response += element.value

        elif isinstance(element, ast.Placeable):
            if isinstance(element.expression, ast.SelectExpression):
                default_variant = get_default_variant(element.expression.variants)
                response += serialize_value(default_variant.value)
            else:
                response += "{ " + serialize_expression(element.expression) + " }"

    return response


def get_simple_preview(content):
    """
    Return content without modifications if it isn't a valid Fluent message.

    Turn a Fluent message into a simple string, without any syntax sigils. Return the
    most pertinent content that can be found in the message, without the ID, attributes
    or selectors.
    """
    translation_ast = parser.parse_entry(content)

    # Non-FTL string or string with an error
    if isinstance(translation_ast, ast.Junk):
        return content

    # Value: use entire AST
    if translation_ast.value:
        tree = translation_ast

    # Attributes (must be present in valid AST if value isn't):
    # use AST of the first attribute
    else:
        tree = translation_ast.attributes[0]

    return serialize_value(tree.value)


def is_plural_expression(expression):
    from pontoon.base.models import Locale

    CLDR_PLURALS = [c for _, c in Locale.CLDR_PLURALS]

    if isinstance(expression, ast.SelectExpression):
        return all(
            isinstance(variant.key, ast.NumberLiteral)
            or variant.key.name in CLDR_PLURALS
            for variant in expression.variants
        )

    return False


def create_locale_plural_variants(node, locale):
    if not is_plural_expression(node):
        return

    variants = []
    source_plurals = {}
    default = None

    for variant in node.variants:
        key = variant.key
        if isinstance(key, ast.NumberLiteral):
            variants.append(variant)
        else:
            source_plurals[key.name] = variant
        if variant.default:
            default = variant

    for plural in locale.cldr_plurals_list():
        if plural in source_plurals.keys():
            variant = source_plurals[plural]
        else:
            variant = copy.deepcopy(default)
            variant.key.name = plural
        variant.default = False
        variants.append(variant)

    variants[-1].default = True

    node.variants = variants
