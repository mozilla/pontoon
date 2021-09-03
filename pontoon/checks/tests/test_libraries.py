from textwrap import dedent
from unittest.mock import patch, MagicMock, ANY

import pytest

from pontoon.base.models import Resource
from pontoon.checks.libraries import run_checks


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
    mock.resource.format = Resource.Format.PROPERTIES
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
    mock.resource.format = Resource.Format.DTD
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
    mock.resource.format = Resource.Format.PROPERTIES
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
    mock.resource.format = Resource.Format.FTL
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
