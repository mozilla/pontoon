import pytest

from collections import OrderedDict
from fluent.syntax import FluentParser
from textwrap import dedent

from pontoon.base.fluent import (
    get_simple_preview,
    is_plural_expression,
)


parser = FluentParser()


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
