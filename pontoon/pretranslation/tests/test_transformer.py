import pytest
from fluent.syntax import FluentParser, FluentSerializer
from textwrap import dedent

from pontoon.pretranslation.transformer import (
    PretranslationTransformer,
    create_locale_plural_variants,
)


def visit(src):
    def callback(str, locale):
        return (str, locale)

    ast = FluentParser().parse_entry(dedent(src))
    PretranslationTransformer("xx", callback).visit(ast)
    return ast


def test_transformer_value_single_element():
    # Do not modify value with single element
    res = visit(
        """
        title = My Title
    """,
    )

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "My Title"


def test_transformer_attribute_single_element():
    # Do not modify attributes with single element
    res = visit(
        """
        title =
            .foo = Bar
    """
    )

    assert len(res.attributes) == 1
    assert len(res.attributes[0].value.elements) == 1
    assert res.attributes[0].value.elements[0].value == "Bar"


def test_transformer_single_select_expression():
    # Do not modify value with a single select expression
    res = visit(
        """
        my-entry =
            { PLATFORM() ->
                [variant] Hello!
                *[another-variant] World!
            }
    """
    )

    assert len(res.value.elements) == 1
    assert (
        res.value.elements[0].expression.variants[0].value.elements[0].value == "Hello!"
    )
    assert (
        res.value.elements[0].expression.variants[1].value.elements[0].value == "World!"
    )


def test_transformer_value_several_elements():
    # Flatten value with several elements
    res = visit(
        """
        title = My { $awesome } Title
    """
    )

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "My { $awesome } Title"


def test_transformer_attribute_several_elements():
    # Flatten attribute with several elements
    res = visit(
        """
        title =
            .foo = Bar { -foo } Baz
    """
    )

    assert len(res.attributes) == 1
    assert len(res.attributes[0].value.elements) == 1
    assert res.attributes[0].value.elements[0].value == "Bar { -foo } Baz"


def test_transformer_value_and_attributes():
    # Flatten value and attributes
    res = visit(
        """
        batman = The { $dark } Knight
            .weapon = Brain and { -wayne-enterprise }
            .history = Lost { 2 } parents, has { 1 } "$alfred"
    """
    )

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "The { $dark } Knight"

    assert len(res.attributes) == 2

    assert len(res.attributes[0].value.elements) == 1
    assert (
        res.attributes[0].value.elements[0].value == "Brain and { -wayne-enterprise }"
    )

    assert len(res.attributes[1].value.elements) == 1
    assert (
        res.attributes[1].value.elements[0].value
        == 'Lost { 2 } parents, has { 1 } "$alfred"'
    )


def test_transformer_callback():
    def callback(str, locale):
        return ("res: " + str, "yy")

    transformer = PretranslationTransformer("en", callback)
    ast = FluentParser().parse_entry("title = My Title\n")
    transformer.visit(ast)

    assert len(transformer.services) == 1
    assert transformer.services[0] == "yy"

    assert len(ast.value.elements) == 1
    assert ast.value.elements[0].value == "res: My Title"


@pytest.mark.django_db
def test_create_locale_plural_variants(locale_a):
    # Create default locale plural variants
    input = dedent(
        """
        my-entry =
            { $num ->
                [0] Yo!
                [one] Hello!
               *[other] { reference } World!
            }
    """
    )

    parser = FluentParser()
    message = parser.parse_entry(input)
    expression = message.value.elements[0].expression

    locale_a.cldr_plurals = "1,2,3,5"
    create_locale_plural_variants(expression, locale_a)

    expected = dedent(
        """
        my-entry =
            { $num ->
                [0] Yo!
                [one] Hello!
                [two] { reference } World!
                [few] { reference } World!
               *[other] { reference } World!
            }
    """
    )

    serializer = FluentSerializer()
    assert serializer.serialize_entry(message) == serializer.serialize_entry(
        parser.parse_entry(expected)
    )
