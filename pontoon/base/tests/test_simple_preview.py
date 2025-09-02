from textwrap import dedent

import pytest

from pontoon.base.simple_preview import get_simple_preview


FLUENT_TRANSLATION_TESTS = {
    "empty": ("", ""),
    "non-ftl": ("Simple string", "Simple string"),
    "simple": ("key = Simple string", "Simple string"),
    "multiline": (
        dedent("""\
                    key =
                        Simple String
                        In Multiple
                        Lines
                    """),
        "Simple String\nIn Multiple\nLines",
    ),
    "plural": (
        dedent("""\
                    key =
                        { $number ->
                            [1] Simple String
                        *[other] Other Simple String
                        }
                    """),
        "Other Simple String",
    ),
    "wrapped-expression": (
        dedent("""\
                    key =
                        Anne liked your comment on { $photo_count ->
                            [male] his
                            [female] her
                        *[other] their
                        } post.
                    """),
        "Anne liked your comment on their post.",
    ),
    "attribute": (
        dedent("""\
                    key =
                        .placeholder = Simple String
                    """),
        "Simple String",
    ),
    "attributes": (
        dedent("""\
                    key =
                        .attribute = Simple String
                        .other = Other Simple String
                    """),
        "Simple String",
    ),
    "attributes-select-expression": (
        dedent("""\
                    key =
                        .placeholder = { PLATFORM() ->
                            [win] Simple String
                            *[other] Other Simple String
                        }
                    """),
        "Other Simple String",
    ),
    "variable-reference": ("key = { $variable }", "{ $variable }"),
    "message-reference": ("key = { message }", "{ message }"),
    "message-reference-attribute": ("key = { foo.bar }", "{ foo.bar }"),
    "term-reference": ("key = { -term }", "{ -term }"),
    "function-reference": (
        'warning-upgrade = { LINK("Link text", title: "Link title") }Simple String',
        '{ LINK("Link text", title: "Link title") }Simple String',
    ),
    "string-literal": ('key = { "" }', '{ "" }'),
    "number-literal": ("key = { 1 }", "{ 1 }"),
}


GETTEXT_TRANSLATION_TESTS = {
    "empty": ("", ""),
    "simple": ("Simple string", "Simple string"),
    "escape": (r"Literals \{ \}", "Literals { }"),
    "multiline": (
        "Simple String\nIn Multiple\nLines",
        "Simple String\nIn Multiple\nLines",
    ),
    "select": (
        dedent("""\
            .input {$n :number}
            .match $n
            1 {{Simple String}}
            * {{Other Simple String}}
        """),
        "Other Simple String",
    ),
    "variable-reference": ("text {$x @source=|$y|}", "text $y"),
}


@pytest.mark.parametrize("name", FLUENT_TRANSLATION_TESTS)
def test_fluent_simple_preview(name):
    string, expected = FLUENT_TRANSLATION_TESTS[name]
    assert get_simple_preview("fluent", string) == expected


@pytest.mark.parametrize("name", GETTEXT_TRANSLATION_TESTS)
def test_gettext_simple_preview(name):
    string, expected = GETTEXT_TRANSLATION_TESTS[name]
    assert get_simple_preview("gettext", string) == expected
