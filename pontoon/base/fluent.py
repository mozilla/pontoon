from fluent.syntax import ast, FluentParser
from fluent.syntax.serializer import serialize_expression


parser = FluentParser()


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
