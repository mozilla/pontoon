import xml.etree.ElementTree as ET

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

    # Fail if the result is not a valid XML
    ET.fromstring(result)

    # Construct the expected XML
    expected = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE martif SYSTEM "TBXcoreStructV02.dtd">
<martif type="TBX" xml:lang="en-US">
    <martifHeader>
        <fileDesc>
            <titleStmt>
                <title>Sample Title</title>
            </titleStmt>
            <sourceDesc>
                <p>Sample Description</p>
            </sourceDesc>
        </fileDesc>
        <encodingDesc>
            <p type="XCSURI">TBXXCSV02.xcs</p>
        </encodingDesc>
    </martifHeader>
    <text>
        <body>
            <termEntry id="c1">
                <descrip type="context">Sample Usage</descrip>
                <langSet xml:lang="en-US">
                    <ntig>
                        <termGrp>
                            <term>Sample Term</term>
                            <termNote type="partOfSpeech">noun</termNote>
                        </termGrp>
                    </ntig>
                    <descripGrp>
                        <descrip type="definition">Sample Definition</descrip>
                    </descripGrp>
                </langSet>
                <langSet xml:lang="fr-FR">
                    <ntig>
                        <termGrp>
                            <term>Translation</term>
                        </termGrp>
                    </ntig>
                </langSet>
            </termEntry>
        </body>
    </text>
</martif>"""

    # Assert that the generated result matches the expected XML
    assert result.strip() == expected.strip()


def test_build_tbx_v3_file(settings, mock_term_translations):
    settings.TBX_TITLE = "Sample Title"
    settings.TBX_DESCRIPTION = "Sample Description"
    locale = "fr-FR"

    result = "".join(build_tbx_v3_file(mock_term_translations, locale))

    # Fail if the result is not a valid XML
    ET.fromstring(result)

    # Construct the expected XML
    expected = """<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="https://raw.githubusercontent.com/LTAC-Global/TBX-Basic_dialect/master/DCA/TBXcoreStructV03_TBX-Basic_integrated.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="https://raw.githubusercontent.com/LTAC-Global/TBX-Basic_dialect/master/DCA/TBX-Basic_DCA.sch" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>
<tbx style="dca" type="TBX-Basic" xml:lang="en" xmlns="urn:iso:std:iso:30042:ed-2">
    <tbxHeader>
        <fileDesc>
            <titleStmt>
                <title>Sample Title</title>
            </titleStmt>
            <sourceDesc>
                <p>Sample Description</p>
            </sourceDesc>
        </fileDesc>
        <encodingDesc>
            <p type="XCSURI">TBXXCSV02.xcs</p>
        </encodingDesc>
    </tbxHeader>
    <text>
        <body>
            <conceptEntry id="c1">
                <langSec xml:lang="en-US">
                    <termSec>
                        <term>Sample Term</term>
                        <termNote type="partOfSpeech">noun</termNote>
                        <descripGrp>
                            <descrip type="definition">Sample Definition</descrip>
                            <descrip type="context">Sample Usage</descrip>
                        </descripGrp>
                    </termSec>
                </langSec>
                <langSec xml:lang="fr-FR">
                    <termSec>
                        <term>Translation</term>
                    </termSec>
                </langSec>
            </conceptEntry>
        </body>
    </text>
</tbx>"""

    # Assert that the generated result matches the expected XML
    assert result.strip() == expected.strip()
