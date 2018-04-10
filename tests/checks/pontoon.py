from __future__ import absolute_import
import pytest

from mock import MagicMock
from textwrap import dedent

from pontoon.checks.libraries.pontoon import run_checks


@pytest.fixture
def mock_entity_max_length():
    """
    Entity with defined max length of a translation.
    """
    entity = MagicMock()
    entity.comment = dedent("""
    Some Comment
    MAX_LENGTH: 10
    """)
    entity.resource.format = 'ftl'
    yield entity


@pytest.fixture
def mock_entity_lang():
    """
    Entity from a .lang file.
    """
    entity = MagicMock()
    entity.comment = ''
    entity.resource.format = 'lang'
    yield entity


@pytest.fixture
def mock_entity_po():
    """
    Entity from a .po file.
    """
    entity = MagicMock()
    entity.comment = ''
    entity.resource.format = 'po'
    yield entity


@pytest.fixture
def mock_entity_properties():
    """
    Entity from a .properties file.
    """
    entity = MagicMock()
    entity.comment = ''
    entity.resource.format = 'properties'
    yield entity


def test_too_long_translation(mock_entity_max_length):
    """
    Checks should return an error if a translation is too long.
    """
    assert run_checks(
        mock_entity_max_length,
        '0123',
    ) == {}

    assert run_checks(
        mock_entity_max_length,
        '0123456789'
    ) == {}

    assert run_checks(
        mock_entity_max_length,
        '0123456789Too long'
    ) == {'pErrors': ['Translation too long.']}


def test_empty_translations(mock_entity_properties, mock_entity_po):
    """
    Empty translations shouldn't be allowed for some of extensions.
    """
    assert run_checks(
        mock_entity_po,
        ''
    ) == {
        'pErrors': [u'Empty translations cannot be submitted.']
    }

    assert run_checks(
        mock_entity_properties,
        ''
    ) == {}


def test_lang_newlines(mock_entity_lang, mock_entity_po):
    """Newlines aren't allowes in lang files"""
    assert run_checks(
        mock_entity_lang,
        'aaa\nbbb'
    ) == {
        'pErrors': [u'Newline characters are not allowed.']
    }

    assert run_checks(
        mock_entity_po,
        'aaa\nbbb'
    ) == {}
