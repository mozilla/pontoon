from collections import OrderedDict

import pytest

from datetime import timedelta

from pontoon.base.templatetags.helpers import (
    as_simple_translation,
    format_datetime,
    format_timedelta,
    nospam,
    to_json,
    metric_prefix,
    get_syntax_type,
    is_simple_single_attribute_message,
    get_reconstructed_message,
)

from fluent.syntax import FluentParser
from pontoon.base.utils import aware_datetime

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

GET_SYNTAX_TYPE_TESTS = [
    {"input": "my-entry = Hello!", "output": "simple"},
    {
        "input": """
my-entry =
    Multi
    line
    value.""",
        "output": "simple",
    },
    {
        "input": 'my-entry = Today is { DATETIME($date, month: "long", year: "numeric", day: "numeric") }',
        "output": "simple",
    },
    {"input": "-my-entry = Hello!", "output": "simple"},
    {"input": "my-entry = Term { -term } Reference", "output": "simple"},
    {"input": "my-entry = { my_id }", "output": "simple"},
    {"input": "my-entry = { my_id.title }", "output": "simple"},
    {"input": 'my-entry = { "" }', "output": "simple"},
    {"input": "my-entry = { 5 }", "output": "simple"},
    {"input": "my-entry = \n    .an-atribute = Hello!", "output": "simple"},
    {"input": "my-entry = World\n    .an-atribute = Hello!", "output": "rich"},
    {
        "input": """
my-entry =
    .an-atribute = Hello!
    .another-atribute = World!""",
        "output": "rich",
    },
    {
        "input": """
my-entry =
    { PLATFORM() ->
        [variant] Hello!
        *[another-variant] World!
    }""",
        "output": "rich",
    },
    {
        "input": """
my-entry =
    There { $num ->
        [one] is one email
       *[other] are many emails
    } for { $gender ->
       *[masculine] him
        [feminine] her
    }""",
        "output": "rich",
    },
    {
        "input": """
my-entry =
    .label =
        { PLATFORM() ->
            [macos] Choose
           *[other] Browse
        }
    .accesskey =
        { PLATFORM() ->
            [macos] e
           *[other] o
        }""",
        "output": "rich",
    },
    {
        "input": """
my-entry =
    { $gender ->
       *[masculine]
            { $num ->
                [one] There is one email for her
               *[other] There are many emails for her
            }
        [feminine]
            { $num ->
                [one] There is one email for him
               *[other] There are many emails for him
            }
    }""",
        "output": "complex",
    },
]

SIMPLE_SINGLE_ATTRIBUTE_TESTS = OrderedDict(
    (
        ("single-attribute", ("my-entry =\n    .an-atribute = Hello!", True)),
        (
            "string-with-text",
            ("my-entry = Something\n    .an-atribute = Hello!", False),
        ),
        (
            "string-with-several-attributes",
            (
                "my-entry =\n    .an-atribute = Hello!\n    .two-attrites = World!",
                False,
            ),
        ),
    )
)

GET_RECONSTRUCTED_MESSAGE_TESTS = test_cases = OrderedDict(
    [
        (
            "simple-message",
            {
                "original": "title = Marvel Cinematic Universe",
                "translation": "Univers cinématographique Marvel",
                "expected": "title = Univers cinématographique Marvel",
            },
        ),
        (
            "single-attribute",
            {
                "original": "spoilers =\n    .who-dies = Who dies?",
                "translation": "Qui meurt ?",
                "expected": "spoilers =\n    .who-dies = Qui meurt ?",
            },
        ),
        (
            "multiline-simple-message",
            {
                "original": "time-travel = They discovered Time Travel",
                "translation": "Ils ont inventé le\nvoyage temporel",
                "expected": "time-travel =\n    Ils ont inventé le\n    voyage temporel",
            },
        ),
        (
            "multiline-single-attribute",
            {
                "original": "slow-walks =\n    .title = They walk in slow motion",
                "translation": "Ils se déplacent\nen mouvement lents",
                "expected": "slow-walks =\n    .title =\n        Ils se déplacent\n        en mouvement lents",
            },
        ),
        (
            "leading-dash-term",
            {
                "original": "-my-term = MyTerm",
                "translation": "Mon Terme",
                "expected": "-my-term = Mon Terme",
            },
        ),
        (
            "only-first-text-element",
            {
                "original": "stark = Tony Stark\n    .hero = IronMan\n    .hair = black",
                "translation": "Anthony Stark",
                "expected": "stark = Anthony Stark",
            },
        ),
        (
            "not-duplicating-terms",
            {
                "original": "with-term = I am { -term }",
                "translation": "Je suis { -term }",
                "expected": "with-term = Je suis { -term }",
            },
        ),
    ]
)


@pytest.mark.parametrize("k", SIMPLE_TRANSLATION_TESTS)
def test_helper_as_simple_translation(k):
    string, expected = SIMPLE_TRANSLATION_TESTS[k]
    assert as_simple_translation(string) == expected


def test_helper_to_json():
    obj = {
        "a": "foo",
        "b": aware_datetime(2015, 1, 1),
    }
    string = '{"a": "foo", "b": "2015-01-01T00:00:00Z"}'
    assert to_json(obj) == string


def test_helper_base_metric_prefix():
    assert metric_prefix(123) == "123"
    assert metric_prefix(1234) == "1.2k"
    assert metric_prefix(759878) == "759.9k"
    assert metric_prefix(299792458) == "299.8M"


def test_helper_base_format_dt_none():
    assert format_datetime(None) == "---"


def test_helper_base_format_dt_custom():
    datetime = aware_datetime(2015, 1, 1, 5, 7)
    assert format_datetime(datetime, "%H:%M") == "05:07"


@pytest.mark.django_db
def test_helper_base_format_dt_builtin(settings):
    """
    Test that there exist built-in formats. We're not interested in
    testing "all" of them, just that the capability exists.
    """
    settings.TIME_ZONE = "UTC"
    datetime = aware_datetime(2015, 1, 1, 5, 7)
    assert format_datetime(datetime, "time") == "05:07 UTC"


def test_helper_base_format_timedelta_none(settings):
    assert format_timedelta(None) == "---"


def test_helper_base_format_timedelta_seconds(settings):
    assert format_timedelta(timedelta(seconds=5)) == "5 seconds"


def test_helper_base_format_timedelta_minutes(settings):
    duration = timedelta(minutes=1, seconds=7)
    assert format_timedelta(duration) == "1 minutes, 7 seconds"


def test_helper_base_format_timedelta_days(settings):
    duration = timedelta(days=2, minutes=1, seconds=8)
    assert format_timedelta(duration) == "2 days, 1 minutes, 8 seconds"


def test_helper_base_format_timedelta_0(settings):
    assert format_timedelta(timedelta(seconds=0)) == "0 seconds"


def test_helper_base_nospam_unicode(settings):
    assert str(nospam("<łążźćń>")) == "&lt;łążźćń&gt;"


def test_helper_base_nospam_escape(settings):
    assert str(nospam("<>'\"@&")) == "&lt;&gt;&#x27;&quot;&#64;&amp;"


def test_get_syntax_type():
    for test_case in GET_SYNTAX_TYPE_TESTS:
        input = test_case["input"]
        expected_output = test_case["output"]
        assert get_syntax_type(input) == expected_output


@pytest.mark.parametrize("k", SIMPLE_SINGLE_ATTRIBUTE_TESTS)
def test_is_simple_single_attribute_message(k):
    string, expected = SIMPLE_SINGLE_ATTRIBUTE_TESTS[k]
    assert is_simple_single_attribute_message(parser.parse_entry(string)) == expected


@pytest.mark.parametrize("k", GET_RECONSTRUCTED_MESSAGE_TESTS)
def test_get_reconstructed_message(k):
    result = get_reconstructed_message(
        GET_RECONSTRUCTED_MESSAGE_TESTS[k]["original"],
        GET_RECONSTRUCTED_MESSAGE_TESTS[k]["translation"],
    )
    assert result == GET_RECONSTRUCTED_MESSAGE_TESTS[k]["expected"]
