from textwrap import dedent
from unittest.mock import ANY, MagicMock, patch

import pytest

from pontoon.base.models import Resource
from pontoon.checks.libraries import run_checks


@pytest.fixture
def run_tt_checks_mock():
    with patch("pontoon.checks.libraries.translate_toolkit.run_checks") as mock:
        yield mock


def test_ignore_warnings():
    """
    Check if logic of ignore_warnings works when there are errors.
    """

    # Mock of entity from a .properties file.
    mock = MagicMock()
    mock.resource.path = "file.properties"
    mock.resource.format = Resource.Format.PROPERTIES
    mock.resource.all.return_value = []
    mock.string = "Example string"
    mock.comment = "Localization_and_Plurals"

    assert run_checks(
        mock,
        "en-US",
        "plural1;plural2;plural3;plural4;plural5",
        True,
    ) == {
        "clWarnings": ["expecting 2 plurals, found 5"],
        "ttWarnings": ["Simple capitalization", "Starting capitalization"],
    }

    # Warnings can be ignored for Translate Toolkit if user decides to do so
    assert run_checks(
        mock,
        "en-US",
        "plural1;plural2;plural3;plural4;plural5",
        False,
    ) == {"clWarnings": ["expecting 2 plurals, found 5"]}


def test_invalid_resource_compare_locales():
    """
    Unsupported resource shouldn't raise an error.
    """

    # Mock of entity from a resource with unsupported filetype.
    mock = MagicMock()
    mock.resource.path = "file.invalid"
    mock.resource.format = "invalid"
    mock.resource.all.return_value = []
    mock.string = "Example string"
    mock.comment = ""

    assert run_checks(mock, "en-US", "Translation", False) == {}


def test_tt_disabled_checks_properties(run_tt_checks_mock):
    """
    Check if overlapping checks are disabled in Translate Toolkit.
    """

    # Mock of entity from a .properties file.
    mock = MagicMock()
    mock.resource.path = "file.properties"
    mock.resource.format = Resource.Format.PROPERTIES
    mock.resource.all.return_value = []
    mock.string = "Example string"
    mock.comment = ""

    assert run_checks(mock, "en-US", "invalid translation \\q", True) == {
        "clWarnings": ["unknown escape sequence, \\q"]
    }
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


def test_tt_disabled_checks_dtd(run_tt_checks_mock):
    """
    Check if overlapping checks are disabled in Translate Toolkit.
    """

    # Mock of entity from a .dtd file.
    mock = MagicMock()
    mock.resource.path = "file.dtd"
    mock.resource.format = Resource.Format.DTD
    mock.resource.all.return_value = []
    mock.string = "Example string"
    mock.key = ["entity_dtd"]
    mock.comment = ""

    assert run_checks(mock, "en-US", "Translated string", True) == {}
    assert not run_tt_checks_mock.assert_called_with(
        ANY, ANY, ANY, {"acronyms", "gconf", "kdecomments", "untranslated"}
    )


def test_tt_gettext_checks():
    entity = MagicMock()
    entity.resource.path = "file.po"
    entity.resource.format = Resource.Format.GETTEXT
    entity.resource.all.return_value = []
    entity.string = dedent("""\
        .input {$n :number}
        .match $n
        one {{One user}}
        * {{%(count)s Users}}""")
    entity.comment = ""
    string = dedent("""\
        .input {$n :number}
        .match $n
        one {{One user}}
        two {{two: %(count)s Users }}
        * {{other: %(count)s Users}}""")
    checks = run_checks(entity, "en-US", string=string, use_tt_checks=True)

    # one: Unchanged
    # two: Ending whitespace, Starting punctuation
    # *: Starting punctuation
    assert checks == {
        "ttWarnings": ["Unchanged", "Ending whitespace", "Starting punctuation"]
    }


def test_tt_android_plural_checks():
    entity = MagicMock()
    entity.resource.path = "strings.xml"
    entity.resource.format = Resource.Format.ANDROID
    entity.resource.all.return_value = []
    entity.string = dedent("""\
        .input {$n :number}
        .match $n
        * {{{$n @source=|%d|} Users}}""")
    entity.comment = ""
    string = dedent("""\
        .input {$n :number}
        .match $n
        one {{one: {$n @source=|%d|} User}}
        two {{two: {$n @source=|%d|} Users }}
        * {{other: {$n @source=|%d|} Users}}""")
    checks = run_checks(entity, "en-US", string=string, use_tt_checks=True)

    # one: Not in source
    # two: Starting punctuation, Ending whitespace
    # *: Starting punctuation
    assert checks == {"ttWarnings": ["Starting punctuation", "Ending whitespace"]}
