# -*- coding: utf-8 -*-
import os
from datetime import datetime

import pytest
from lxml import etree

from django.urls import reverse

from pontoon.base.utils import build_translation_memory_file


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
        assert validated_xml == etree.tostring(etree.fromstring(expected_xml))


@pytest.mark.django_db
def test_view_tmx_locale_file_dl(client, entity_a, locale_a):
    """By download the data."""
    url = reverse(
        "pontoon.download_tmx", args=(locale_a.code, entity_a.resource.project.slug,)
    )
    response = client.get(url)
    assert response.status_code == 200
    _check_xml(b"".join(response.streaming_content))


@pytest.mark.django_db
def test_view_tmx_bad_params(client, entity_a, locale_a, settings_debug):
    """Validate locale code and don't return data."""
    url = reverse("pontoon.download_tmx", args=("invalidlocale", "invalidproject",))
    response = client.get(url)
    assert response.status_code == 404

    url = reverse("pontoon.download_tmx", args=(locale_a, "invalidproject",))
    response = client.get(url)
    assert response.status_code == 404


def test_view_tmx_empty_file():
    data_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data",)
    filepath = "tmx/no_entries.tmx"

    with open(os.path.join(data_root, filepath), "r", encoding="utf-8") as f:
        xml = f.read()

    tmx_contents = build_translation_memory_file(datetime(2010, 1, 1), "sl", ())
    _check_xml(
        "".join(tmx_contents).encode("utf-8"),
        xml,
        os.path.join(data_root, "tmx/tmx14.dtd"),
    )


def test_view_tmx_valid_entries():
    data_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data",)
    filepath = "tmx/valid_entries.tmx"

    with open(os.path.join(data_root, filepath), "r", encoding="utf-8") as f:
        xml = f.read()

    tmx_contents = build_translation_memory_file(
        datetime(2010, 1, 1),
        "sl",
        (
            (
                "aa/bb/ccc",
                "xxx",
                "source string",
                "translation",
                "Pontoon App",
                "pontoon",
            ),
            # Test escape of characters
            (
                "aa/bb/ccc",
                'x&y&z#"',
                "source string",
                "translation",
                "Pontoon & App",
                "pontoon",
            ),
            # Handle unicode characters
            (
                "aa/bb/ccc",
                "xxx",
                "source string łążśźć",
                "translation łążśźć",
                "pontoon",
                "pontoon",
            ),
            # Handle html content
            (
                "aa/bb/ccc",
                "xxx",
                "<p>source <strong>string</p>",
                "<p>translation łążśźć</p>",
                "pontoon",
                "pontoon",
            ),
        ),
    )
    _check_xml(
        "".join(tmx_contents).encode("utf-8"),
        xml,
        os.path.join(data_root, "tmx/tmx14.dtd"),
    )
