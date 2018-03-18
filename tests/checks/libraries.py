import json

import pytest

from textwrap import dedent
from mock import patch, MagicMock, ANY

from pontoon.checks.libraries import run_checks


@pytest.yield_fixture
def run_tt_checks_mock():
    with patch('pontoon.checks.libraries.translatetoolkit.run_checks') as mock:
        yield mock


@pytest.yield_fixture()
def entity_properties_mock():
    """
    Mock of entity from a .properties file.
    """
    mock = MagicMock()
    mock.resource.path = 'file.properties'
    mock.resource.format = 'properties'
    mock.resource.all.return_value = []
    mock.string = 'Example string'
    mock.comment = ''

    yield mock


@pytest.yield_fixture()
def entity_invalid_resource_mock():
    """
    Mock of entity from a resource with unsupported filetype.
    """
    mock = MagicMock()
    mock.resource.path = 'file.invalid'
    mock.resource.format = 'invalid'
    mock.resource.all.return_value = []
    mock.string = 'Example string'
    mock.comment = ''

    yield mock


@pytest.yield_fixture()
def entity_ftl_mock():
    """
    Mock of entity from a  a .ftl file.
    """
    mock = MagicMock()
    mock.resource.path = 'file.ftl'
    mock.resource.format = 'ftl'
    mock.resource.all.return_value = []
    mock.string = dedent("""
    windowTitle = Untranslated string
        .pontoon = is cool
    """)
    mock.comment = ''
    yield mock


@pytest.yield_fixture()
def locale_mock():
    mock = MagicMock()
    mock.code = 'en-US'
    yield mock


def test_ignore_warnings(
    entity_ftl_mock,
    locale_mock
):
    """
    Check if logic of ignore_warnings works when there are errors.
    """
    assert run_checks(
        entity_ftl_mock,
        locale_mock,
        entity_ftl_mock.string,
        dedent("""
        windowTitle = Translated string
            .pontoon = is cool
            .pontoon = is cool2
        """),
        False,
        False,
    ).content == json.dumps({
        'failedChecks': {
            'clWarnings': ['Attribute "pontoon" occurs 2 times'],
            'ttWarnings': ['Double spaces', 'Newlines']
        },
        'same': False,
    })

    # Warnings can be ignored for Translate Toolkit if user decides to do so
    assert run_checks(
        entity_ftl_mock,
        locale_mock,
        entity_ftl_mock.string,
        dedent("""
        windowTitle = Translated string
            .pontoon = is  cool
        """),
        True,
        False,
    ) is None

    # Quality check should always return critical errors
    assert run_checks(
        entity_ftl_mock,
        locale_mock,
        entity_ftl_mock.string,
        dedent("""
        windowTitle
            .pontoon = is cool
            .pontoon = is cool2
        """),
        True,
        False,
    ).content == json.dumps({
        'failedChecks': {
            'clErrors': ['Missing value'],
            'clWarnings': ['Attribute "pontoon" occurs 2 times'],
            'ttWarnings': ['Double spaces', 'Newlines'],
        },
        'same': False
    })


def test_invalid_resource_compare_locales(
    entity_invalid_resource_mock,
    locale_mock,
):
    """
    Unsupported resource shouldn't raise an error.
    """
    assert run_checks(
        entity_invalid_resource_mock,
        locale_mock,
        entity_invalid_resource_mock.string,
        'Translation',
        False,
        False
    ) is None


def test_tt_disabled_checks(
    entity_ftl_mock,
    entity_properties_mock,
    locale_mock,
    run_tt_checks_mock
):
    """
    Check if overlapping checks are disabled in Translate Toolkit.
    """
    assert run_checks(
        entity_properties_mock,
        locale_mock,
        entity_properties_mock.string,
        'invalid translation \q',
        False,
        False,
    ).content == json.dumps({
        'failedChecks': {
            'clWarnings': [
                'unknown escape sequence, \q'
            ]
        },
        'same': False,
    })

    run_tt_checks_mock.assert_called_with(
        ANY,
        ANY,
        ANY,
        {'escapes', 'nplurals', 'printf'}
    )

    assert run_checks(
        entity_ftl_mock,
        locale_mock,
        entity_ftl_mock.string,
        dedent("""
        windowTitle = Translated string
            .pontoon = is cool
        """),
        False,
        False
    ) is None
    run_tt_checks_mock.assert_called_with(
        ANY,
        ANY,
        ANY,
        set()
    )
