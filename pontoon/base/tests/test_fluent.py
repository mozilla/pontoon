import pytest

from collections import OrderedDict
from fluent.syntax import FluentParser, FluentSerializer
from textwrap import dedent

from pontoon.base.fluent import (
    FlatTransformer,
    get_simple_preview,
    is_plural_expression,
    create_locale_plural_variants,
)


parser = FluentParser()
serializer = FluentSerializer()
transformer = FlatTransformer()


MULTILINE_SOURCE = """key =
    Simple String
    In Multiple
    Lines"""
PLURAL_SOURCE = """key =
    { $number ->
        [1] Simple String
       *[other] Other Simple String
    }"""
WRAPPED_SELECT_SOURCE = """key =
    Anne liked your comment on { $photo_count ->
        [male] his
        [female] her
       *[other] their
    } post."""
ATTRIBUTE_SOURCE = """key =
    .placeholder = Simple String"""
ATTRIBUTES_SOURCE = """key =
    .attribute = Simple String
    .other = Other Simple String"""
ATTRIBUTE_SELECT_SOURCE = """key =
    .placeholder = { PLATFORM() ->
        [win] Simple String
        *[other] Other Simple String
    }"""

SIMPLE_TRANSLATION_TESTS = OrderedDict(
    (
        ("empty", ("", "")),
        ("non-ftl", ("Simple string", "Simple string")),
        ("simple", ("key = Simple string", "Simple string")),
        ("multiline", (MULTILINE_SOURCE, "Simple String\nIn Multiple\nLines")),
        ("plural", (PLURAL_SOURCE, "Other Simple String")),
        (
            "wrapped-expression",
            (WRAPPED_SELECT_SOURCE, "Anne liked your comment on their post."),
        ),
        ("attribute", (ATTRIBUTE_SOURCE, "Simple String")),
        ("attributes", (ATTRIBUTES_SOURCE, "Simple String")),
        (
            "attributes-select-expression",
            (ATTRIBUTE_SELECT_SOURCE, "Other Simple String"),
        ),
        ("variable-reference", ("key = { $variable }", "{ $variable }")),
        ("message-reference", ("key = { message }", "{ message }")),
        ("message-reference-attribute", ("key = { foo.bar }", "{ foo.bar }")),
        ("term-reference", ("key = { -term }", "{ -term }")),
        (
            "function-reference",
            (
                'warning-upgrade = { LINK("Link text", title: "Link title") }Simple String',
                '{ LINK("Link text", title: "Link title") }Simple String',
            ),
        ),
        ("string-literal", ('key = { "" }', '{ "" }')),
        ("number-literal", ("key = { 1 }", "{ 1 }")),
    )
)


def test_flat_transformer_value_single_element():
    # Do not modify value with single element
    source_string = dedent(
        """
        title = My Title
    """
    )

    res = parser.parse_entry(source_string)
    transformer.visit(res)

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "My Title"


def test_flat_transformer_attribute_single_element():
    # Do not modify attributes with single element
    source_string = dedent(
        """
        title =
            .foo = Bar
    """
    )

    res = parser.parse_entry(source_string)
    transformer.visit(res)

    assert len(res.attributes) == 1
    assert len(res.attributes[0].value.elements) == 1
    assert res.attributes[0].value.elements[0].value == "Bar"


def test_flat_transformer_single_select_expression():
    # Do not modify value with a single select expression
    source_string = dedent(
        """
        my-entry =
            { PLATFORM() ->
                [variant] Hello!
                *[another-variant] World!
            }
    """
    )

    res = parser.parse_entry(source_string)
    transformer.visit(res)

    assert len(res.value.elements) == 1
    assert (
        res.value.elements[0].expression.variants[0].value.elements[0].value == "Hello!"
    )
    assert (
        res.value.elements[0].expression.variants[1].value.elements[0].value == "World!"
    )


def test_flat_transformer_value_several_elements():
    # Flatten value with several elements
    source_string = dedent(
        """
        title = My { $awesome } Title
    """
    )

    res = parser.parse_entry(source_string)
    transformer.visit(res)

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "My { $awesome } Title"


def test_flat_transformer_attribute_several_elements():
    # Flatten attribute with several elements
    source_string = dedent(
        """
        title =
            .foo = Bar { -foo } Baz
    """
    )

    res = parser.parse_entry(source_string)
    transformer.visit(res)

    assert len(res.attributes) == 1
    assert len(res.attributes[0].value.elements) == 1
    assert res.attributes[0].value.elements[0].value == "Bar { -foo } Baz"


def test_flat_transformer_value_and_attributes():
    # Flatten value and attributes
    source_string = dedent(
        """
        batman = The { $dark } Knight
            .weapon = Brain and { -wayne-enterprise }
            .history = Lost { 2 } parents, has { 1 } "$alfred"
    """
    )

    res = parser.parse_entry(source_string)
    transformer.visit(res)

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


@pytest.mark.parametrize("k", SIMPLE_TRANSLATION_TESTS)
def test_get_simple_preview(k):
    string, expected = SIMPLE_TRANSLATION_TESTS[k]
    assert get_simple_preview(string) == expected


def test_is_plural_expression_not_select_expression():
    # Return False for elements that are not select expressions
    input = dedent(
        """
        my-entry = Hello!
    """
    )

    message = parser.parse_entry(input)
    element = message.value.elements[0]

    assert is_plural_expression(element) is False


def test_is_plural_expression_all_cldr_plurals():
    # Return True if all variant keys are CLDR plurals
    input = dedent(
        """
        my-entry =
            { $num ->
                [one] Hello!
               *[two] World!
            }`
    """
    )

    message = parser.parse_entry(input)
    element = message.value.elements[0]

    assert is_plural_expression(element.expression) is True


def test_is_plural_expression_all_numbers():
    # Return True if all variant keys are numbers
    input = dedent(
        """
        my-entry =
            { $num ->
                [1] Hello!
               *[2] World!
            }`
    """
    )

    message = parser.parse_entry(input)
    element = message.value.elements[0]

    assert is_plural_expression(element.expression) is True


def test_is_plural_expression_one_cldr_plural_one_number():
    # Return True if one variant key is a CLDR plural and the other is a number
    input = dedent(
        """
        my-entry =
            { $num ->
                [one] Hello!
               *[1] World!
            }`
    """
    )

    message = parser.parse_entry(input)
    element = message.value.elements[0]

    assert is_plural_expression(element.expression) is True


def test_is_plural_expression_one_cldr_plural_one_something_else():
    # Return False if one variant key is a CLDR plural and the other is neither a CLDR plural nor a number
    input = dedent(
        """
        my-entry =
            { $num ->
                [one] Hello!
               *[variant] World!
            }`
    """
    )

    message = parser.parse_entry(input)
    element = message.value.elements[0]

    assert is_plural_expression(element.expression) is False


def test_is_plural_expression_neither_cldr_plural_nor_number():
    # Return False if neither variant key is a CLDR plural nor a number
    input = dedent(
        """
        my-entry =
            { $num ->
                [variant] Hello!
               *[another-variant] World!
            }`
    """
    )

    message = parser.parse_entry(input)
    element = message.value.elements[0]

    assert is_plural_expression(element.expression) is False


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

    assert serializer.serialize_entry(message) == serializer.serialize_entry(
        parser.parse_entry(expected)
    )
