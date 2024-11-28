from unittest.mock import MagicMock

import pytest

from pontoon.terminology.utils import build_tbx_v2_file, build_tbx_v3_file


@pytest.fixture
def mock_term_translations():
    term_mock = MagicMock()
    term_mock.pk = 1
    term_mock.text = "Sample Term"
    term_mock.part_of_speech = "noun"
    term_mock.definition = "Sample Definition"
    term_mock.usage = "Sample Usage"

    translation_mock = MagicMock()
    translation_mock.term = term_mock
    translation_mock.text = "Translation"

    return [translation_mock]


def test_build_tbx_v2_file(settings, mock_term_translations):
    settings.TBX_TITLE = "Sample Title"
    settings.TBX_DESCRIPTION = "Sample Description"
    locale = "fr-FR"

    result = "".join(build_tbx_v2_file(mock_term_translations, locale))

    # Check for expected parts of the XML
    assert '<?xml version="1.0" encoding="UTF-8"?>' in result
    assert "Sample Title" in result
    assert "Sample Description" in result
    assert '<termEntry id="c1">' in result
    assert "Sample Term" in result
    assert "Sample Definition" in result
    assert "Sample Usage" in result
    assert "Translation" in result
    assert "fr-FR" in result


def test_build_tbx_v3_file(settings, mock_term_translations):
    settings.TBX_TITLE = "Sample Title"
    settings.TBX_DESCRIPTION = "Sample Description"
    locale = "fr-FR"

    result = "".join(build_tbx_v3_file(mock_term_translations, locale))

    # Check for expected parts of the XML
    assert '<?xml version="1.0" encoding="UTF-8"?>' in result
    assert "Sample Title" in result
    assert "Sample Description" in result
    assert '<conceptEntry id="c1">' in result
    assert "Sample Term" in result
    assert "Sample Definition" in result
    assert "Sample Usage" in result
    assert "Translation" in result
    assert "fr-FR" in result


def test_xml_format_v2(mock_term_translations):
    locale = "fr-FR"

    result = "".join(build_tbx_v2_file(mock_term_translations, locale))

    # Ensure the XML is correctly formatted for TBX v2
    assert result.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert '<martif type="TBX"' in result
    assert '<termEntry id="c1">' in result
    assert '<langSet xml:lang="fr-FR">' in result
    assert "</martif>" in result


def test_xml_format_v3(mock_term_translations):
    locale = "fr-FR"

    result = "".join(build_tbx_v3_file(mock_term_translations, locale))

    # Ensure the XML is correctly formatted for TBX v3
    assert result.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert '<tbx style="dca" type="TBX-Basic"' in result
    assert '<conceptEntry id="c1">' in result
    assert '<langSec xml:lang="fr-FR">' in result
    assert "</tbx>" in result
