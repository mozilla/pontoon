from fluent.syntax import FluentParser, ast
from fluent.syntax.serializer import serialize_expression

from pontoon.base.models import Resource


parser = FluentParser()


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
                default_variant = next(
                    variant
                    for variant in element.expression.variants
                    if variant.default
                )
                response += serialize_value(default_variant.value)
            else:
                response += "{ " + serialize_expression(element.expression) + " }"

    return response


def get_simple_preview(format: str, string: str):
    """
    Return content without modifications if it isn't a valid Fluent message.

    Turn a Fluent message into a simple string, without any syntax sigils. Return the
    most pertinent content that can be found in the message, without the ID, attributes
    or selectors.
    """
    if format != Resource.Format.FLUENT:
        return string

    translation_ast = parser.parse_entry(string)

    # Non-FTL string or string with an error
    if isinstance(translation_ast, ast.Junk):
        return string

    # Value: use entire AST
    if translation_ast.value:
        tree = translation_ast

    # Attributes (must be present in valid AST if value isn't):
    # use AST of the first attribute
    else:
        tree = translation_ast.attributes[0]

    return serialize_value(tree.value)
