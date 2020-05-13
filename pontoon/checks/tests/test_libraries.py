from __future__ import absolute_import

import pytest

from textwrap import dedent
from mock import patch, MagicMock, ANY

from pontoon.checks.libraries import run_checks, ftl_to_simplified_string


@pytest.yield_fixture
def run_tt_checks_mock():
    with patch("pontoon.checks.libraries.translate_toolkit.run_checks") as mock:
        yield mock


@pytest.yield_fixture()
def entity_properties_mock():
    """
    Mock of entity from a .properties file.
    """
    mock = MagicMock()
    mock.resource.path = "file.properties"
    mock.resource.format = "properties"
    mock.resource.all.return_value = []
    mock.string = "Example string"
    mock.comment = ""

    yield mock


@pytest.yield_fixture()
def entity_dtd_mock():
    """
    Mock of entity from a .dtd file.
    """
    mock = MagicMock()
    mock.resource.path = "file.dtd"
    mock.resource.format = "dtd"
    mock.resource.all.return_value = []
    mock.string = "Example string"
    mock.key = "entity_dtd"
    mock.comment = ""

    yield mock


@pytest.yield_fixture()
def entity_properties_plurals_mock():
    """
    Mock of entity from a .properties file.
    """
    mock = MagicMock()
    mock.resource.path = "file.properties"
    mock.resource.format = "properties"
    mock.resource.all.return_value = []
    mock.string = "Example string"
    mock.comment = "Localization_and_Plurals"

    yield mock


@pytest.yield_fixture()
def entity_invalid_resource_mock():
    """
    Mock of entity from a resource with unsupported filetype.
    """
    mock = MagicMock()
    mock.resource.path = "file.invalid"
    mock.resource.format = "invalid"
    mock.resource.all.return_value = []
    mock.string = "Example string"
    mock.comment = ""

    yield mock


@pytest.yield_fixture()
def entity_ftl_mock():
    """
    Mock of entity from a  a .ftl file.
    """
    mock = MagicMock()
    mock.resource.path = "file.ftl"
    mock.resource.format = "ftl"
    mock.resource.all.return_value = []
    mock.string = dedent(
        """
    windowTitle = Untranslated string
        .pontoon = is cool
    """
    )
    mock.comment = ""
    yield mock


def test_ignore_warnings(entity_properties_plurals_mock,):
    """
    Check if logic of ignore_warnings works when there are errors.
    """
    assert run_checks(
        entity_properties_plurals_mock,
        "en-US",
        entity_properties_plurals_mock.string,
        "plural1;plural2;plural3;plural4;plural5",
        True,
    ) == {
        "clWarnings": ["expecting 2 plurals, found 5"],
        "ttWarnings": ["Simple capitalization", "Starting capitalization"],
    }

    # Warnings can be ignored for Translate Toolkit if user decides to do so
    assert run_checks(
        entity_properties_plurals_mock,
        "en-US",
        entity_properties_plurals_mock.string,
        "plural1;plural2;plural3;plural4;plural5",
        False,
    ) == {"clWarnings": ["expecting 2 plurals, found 5"]}


def test_invalid_resource_compare_locales(entity_invalid_resource_mock,):
    """
    Unsupported resource shouldn't raise an error.
    """
    assert (
        run_checks(
            entity_invalid_resource_mock,
            "en-US",
            entity_invalid_resource_mock.string,
            "Translation",
            False,
        )
        == {}
    )


def test_tt_disabled_checks(
    entity_properties_mock, entity_dtd_mock, run_tt_checks_mock,
):
    """
    Check if overlapping checks are disabled in Translate Toolkit.
    """
    assert run_checks(
        entity_properties_mock,
        "en-US",
        entity_properties_mock.string,
        "invalid translation \\q",
        True,
    ) == {"clWarnings": ["unknown escape sequence, \\q"]}
    run_tt_checks_mock.assert_called_with(
        ANY,
        ANY,
        ANY,
        {
            "escapes",
            "acronyms",
            "printf",
            "gconf",
            "kdecomments",
            "nplurals",
            "untranslated",
        },
    )

    assert (
        run_checks(
            entity_dtd_mock,
            "en-US",
            entity_properties_mock.string,
            "Translated string",
            True,
        )
        == {}
    )
    assert not run_tt_checks_mock.assert_called_with(
        ANY, ANY, ANY, {"acronyms", "gconf", "kdecomments", "untranslated"}
    )


def test_ftl_to_simplified_string():
    """
    Check that the ftl_to_simplified_string helper serializes simple and complex Fluent messages down to
    simplified, translate-toolkit-ready strings
    """

    assert (
        ftl_to_simplified_string(
            dedent(
                """
        message-one = Welcome
    """
            )
        )
        == "Welcome"
    )

    assert (
        ftl_to_simplified_string(
            dedent(
                """
        message-one = Welcome { $withAVariable }.
    """
            )
        )
        == "Welcome {$withAVariable}."
    )

    assert (
        ftl_to_simplified_string(
            dedent(
                """
        message-one = Welcome
            .withAttribute = with an attribute.
    """
            )
        )
        == "Welcome with an attribute."
    )

    assert (
        ftl_to_simplified_string(
            dedent(
                """
        message-one = Welcome {"with a string literal"}.
    """
            )
        )
        == "Welcome with a string literal."
    )

    assert (
        ftl_to_simplified_string(
            dedent(
                """
        message-one = Welcome {with-a-message-reference}.
    """
            )
        )
        == "Welcome ."
    )

    assert (
        ftl_to_simplified_string(
            dedent(
                """
        message-one = Welcome { $n ->
            [one] with a select expression
            *[other] with { $n } multiple cases
        }.
    """
            )
        )
        == "Welcome {$n} with a select expression with {$n} multiple cases."
    )

    assert (
        ftl_to_simplified_string(
            dedent(
                """
        message-one = Welcome { DATETIME($withAFunctionCall) }.
    """
            )
        )
        == "Welcome {$withAFunctionCall}."
    )


def test_tt_checks_simple_ftl(
    entity_ftl_mock, run_tt_checks_mock,
):
    """
    Check translate toolkit checks for a simple ftl entity
    """

    translated_string = dedent(
        """
    windowTitle = Translated string
        .pontoon = is kewl
    """
    )

    run_checks(
        entity_ftl_mock, "en-US", entity_ftl_mock.string, translated_string, True,
    )

    run_tt_checks_mock.assert_called_with(
        "Untranslated string is cool",
        "Translated string is kewl",
        ANY,
        {
            "acronyms",
            "gconf",
            "kdecomments",
            "untranslated",
            "doublespacing",
            "endwhitespace",
            "escapes",
            "newlines",
            "numbers",
            "printf",
            "singlequoting",
            "startwhitespace",
            "pythonbraceformat",
            "doublequoting",
        },
        None,
        {"varmatches": [("{$", "}")]},
    )
