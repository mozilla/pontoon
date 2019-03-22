# -*- coding: utf-8 -*-
from __future__ import absolute_import
import pytest

from mock import MagicMock

from pontoon.checks.libraries.stored import run_checks


@pytest.fixture()
def get_entity_mock():
    """
    Create an entity mock with comment, resource.path and extension.
    """
    def _f(extension, comment='', string='', allows_empty_translations=False):
        entity = MagicMock()
        entity.comment = comment
        entity.string = string
        entity.resource.format = extension
        entity.resource.path = 'test.' + extension
        entity.resource.allows_empty_translations = allows_empty_translations
        return entity
    yield _f


def test_empty_translations(get_entity_mock):
    """
    Empty translations shouldn't be allowed for some extensions.
    """
    assert run_checks(
        get_entity_mock('properties', allows_empty_translations=True),
        ''
    ) == {
        'pWarnings': [u'Empty translation']
    }
