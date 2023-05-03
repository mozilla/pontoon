import pytest
from fluent.syntax import FluentParser, FluentSerializer
from textwrap import dedent

from pontoon.pretranslation.transformer import (
    PretranslationTransformer,
    create_locale_plural_variants,
)


def visit(src):
    def callback(str, locale, format):
        return (str, locale + format)

    ast = FluentParser().parse_entry(dedent(src))
    transformer = PretranslationTransformer("xx", callback)
    transformer.visit(ast)
    return ast, transformer


def test_transformer_value_single_element():
    # Do not modify value with single element
    res, transformer = visit(
        """
        title = My Title
    """,
    )

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "My Title"

    assert len(transformer.replacements) == 0


def test_transformer_attribute_single_element():
    # Do not modify attributes with single element
    res, transformer = visit(
        """
        title =
            .foo = Bar
    """
    )

    assert len(res.attributes) == 1
    assert len(res.attributes[0].value.elements) == 1
    assert res.attributes[0].value.elements[0].value == "Bar"

    assert len(transformer.replacements) == 0


def test_transformer_single_select_expression():
    # Do not modify value with a single select expression
    res, transformer = visit(
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

    assert len(transformer.replacements) == 0


def test_transformer_value_several_elements():
    # Flatten value with several elements
    res, transformer = visit(
        """
        title = My { $awesome } Title
    """
    )

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "My { $awesome } Title"

    assert len(transformer.replacements) == 1
    assert transformer.replacements[0] == "{ $awesome }"


def test_transformer_attribute_several_elements():
    # Flatten attribute with several elements
    res, transformer = visit(
        """
        title =
            .foo = Bar { -foo } Baz
    """
    )

    assert len(res.attributes) == 1
    assert len(res.attributes[0].value.elements) == 1
    assert res.attributes[0].value.elements[0].value == "Bar { -foo } Baz"

    assert len(transformer.replacements) == 1
    assert transformer.replacements[0] == "{ -foo }"


def test_transformer_value_and_attributes():
    # Flatten value and attributes
    res, transformer = visit(
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

    assert len(transformer.replacements) == 4
    assert transformer.replacements[0] == "{ $dark }"
    assert transformer.replacements[1] == "{ -wayne-enterprise }"
    assert transformer.replacements[2] == "{ 2 }"
    assert transformer.replacements[3] == "{ 1 }"


def test_transformer_callback():
    called = []

    def callback(raw, escaped, locale):
        called.append((raw, escaped))
        return ("res: " + escaped, locale)

    transformer = PretranslationTransformer("yy", callback)
    ast = FluentParser().parse_entry("title = Hello { $world }!\n")
    transformer.visit(ast)

    assert len(ast.value.elements) == 1
    assert ast.value.elements[0].value == "res: Hello { $world }!"

    assert len(transformer.replacements) == 1
    assert transformer.replacements[0] == "{ $world }"

    assert len(transformer.services) == 1
    assert transformer.services[0] == "yy"

    assert len(called) == 1
    assert called[0][0] == 'Hello { $world }!'
    assert called[0][1] == 'Hello <span id="pt-0" translate="no">{ $world }</span>!'


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
