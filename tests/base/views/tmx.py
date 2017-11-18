# -*- coding: utf-8 -*-

import os
from datetime import datetime

import pytest

from lxml import etree

from pontoon.base.utils import build_translation_memory_file

import tests


def _check_xml(xml_content, expected_xml=None, dtd_path=None):
    """Provided xml_content should be a valid XML string
    and be equal to expected_xml.
    """
    validated_xml = etree.tostring(etree.fromstring(xml_content))

    if dtd_path:
        dtd = etree.DTD(dtd_path)
        if not dtd.validate(etree.fromstring(xml_content)):
            raise AssertionError(dtd.error_log)

    if expected_xml is not None:
        assert (
            validated_xml
            == etree.tostring(etree.fromstring(expected_xml)))


@pytest.mark.xfail(reason="Original tests were broken")
@pytest.mark.django_db
def test_view_tmx_locale_file_dl(client, entity0, locale0):
    """By download the data."""
    response = client.get(
        '/{locale}/{project}/{locale}.{project}.tmx'.format(
            locale=locale0.code,
            project=entity0.resource.project.slug))
    assert response.status_code == 200
    _check_xml(
        ''.join(response.streaming_content).encode('utf-8'))


@pytest.mark.django_db
def test_view_tmx_bad_params(client, entity0, locale0, settings_debug):
    """Validate locale code and don't return data."""
    response = client.get(
        '/{locale}/{project}/{locale}.{project}.tmx'.format(
            locale='invalidlocale',
            project='invalidproject'))
    assert response.status_code == 404

    response = client.get(
        '/{locale}/{project}/{locale}.{project}.tmx'.format(
            locale=locale0,
            project='invalidproject'))
    assert response.status_code == 404


@pytest.mark.xfail(reason="Original tests were broken")
@pytest.mark.django_db
def test_view_tmx_empty_file():
    data_root = os.path.join(
        os.path.dirname(os.path.abspath(tests.__file__)),
        'data')
    filepath = 'tmx/no_entries.tmx'
    with open(os.path.join(data_root, filepath), 'rU') as f:
        xml = f.read().decode('utf-8')
    tmx_contents = build_translation_memory_file(
        datetime(2010, 01, 01), 'sl', ())
    _check_xml(
        ''.join(tmx_contents).encode('utf-8'),
        xml,
        os.path.join(data_root, 'tmx/tmx14.dtd'))


@pytest.mark.xfail(reason="Original tests were broken")
@pytest.mark.django_db
def test_view_tmx_valid_entries():
    data_root = os.path.join(
        os.path.dirname(os.path.abspath(tests.__file__)),
        'data')
    filepath = 'tmx/valid_entries.tmx'
    with open(os.path.join(data_root, filepath), 'rU') as f:
        xml = f.read().decode('utf-8')
    tmx_contents = build_translation_memory_file(
        datetime(2010, 01, 01),
        'sl',
        (('aa/bb/ccc',
          'xxx',
          'source string',
          'translation',
          'Pontoon App',
          'pontoon'),
         # Test escape of characters
         ('aa/bb/ccc',
          'x&x&x#"',
          'source string',
          'translation',
          'Pontoon & App',
          'pontoon'),
         # Handle unicode characters
         ('aa/bb/ccc',
          'xxx',
          u'source string łążśźć',
          u'translation łążśźć',
          'pontoon',
          'pontoon'),
         # Handle html content
         ('aa/bb/ccc',
          'xxx',
          u'<p>source <strong>string</p>',
          u'<p>translation łążśźć</p>',
          'pontoon', 'pontoon')))
    _check_xml(
        ''.join(tmx_contents).encode('utf-8'),
        xml,
        os.path.join(data_root, 'tmx/tmx14.dtd'))
