import xml.etree.ElementTree as ET

from unittest.mock import MagicMock

import pytest

from pontoon.terminology.utils import build_tbx_v2_file, build_tbx_v3_file


def find_all(root, tag):
    """Find all elements with the given local name, ignoring any namespace."""
    return [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == tag]


def make_term(pk, text, translation, **kwargs):
    term = MagicMock()
    term.pk = pk
    term.text = text
    term.part_of_speech = "noun"
    term.definition = "Sample Definition"
    term.usage = "Sample Usage"
    term.forbidden = False
    term.do_not_translate = False

    term_translation = MagicMock()
    term_translation.text = translation
    term.filtered_translations = [term_translation]

    for name, value in kwargs.items():
        setattr(term, name, value)

    return term


@pytest.fixture
def mock_terms():
    return [make_term(1, "Sample Term", "Translation")]


def test_build_tbx_v2_file(settings, mock_terms):
    settings.TBX_TITLE = "Sample Title"
    settings.TBX_DESCRIPTION = "Sample Description"
    locale = "fr-FR"

    result = "".join(build_tbx_v2_file(mock_terms, locale))

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


def test_build_tbx_v3_file(settings, mock_terms):
    settings.TBX_TITLE = "Sample Title"
    settings.TBX_DESCRIPTION = "Sample Description"
    locale = "fr-FR"

    result = "".join(build_tbx_v3_file(mock_terms, locale))

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


@pytest.mark.parametrize(
    "build_tbx_file", [build_tbx_v2_file, build_tbx_v3_file], ids=["v2", "v3"]
)
def test_build_tbx_file_do_not_translate(settings, build_tbx_file):
    # A do-not-translate term has no translation in the locale, and is exported
    # with the source text as its translation.
    settings.TBX_TITLE = "Sample Title"
    settings.TBX_DESCRIPTION = "Sample Description"
    term = make_term(1, "Firefox", None, do_not_translate=True)
    term.filtered_translations = []

    result = "".join(build_tbx_file([term], "fr-FR"))

    root = ET.fromstring(result)
    terms = [node.text for node in find_all(root, "term")]
    assert terms == ["Firefox", "Firefox"]


@pytest.mark.parametrize(
    "build_tbx_file", [build_tbx_v2_file, build_tbx_v3_file], ids=["v2", "v3"]
)
def test_build_tbx_file_forbidden(settings, build_tbx_file):
    # A forbidden term is exported as deprecated, so that it can be flagged as
    # such by translation tools.
    settings.TBX_TITLE = "Sample Title"
    settings.TBX_DESCRIPTION = "Sample Description"
    term = make_term(1, "abort", "annullare", forbidden=True)

    result = "".join(build_tbx_file([term], "it"))

    root = ET.fromstring(result)
    notes = {node.get("type"): node.text for node in find_all(root, "termNote")}
    assert notes == {
        "partOfSpeech": "noun",
        "administrativeStatus": "deprecatedTerm-admn-sts",
    }


@pytest.mark.parametrize(
    "build_tbx_file", [build_tbx_v2_file, build_tbx_v3_file], ids=["v2", "v3"]
)
def test_build_tbx_file_skips_untranslated(settings, build_tbx_file):
    # A term that is neither translated in the locale nor do-not-translate has
    # nothing to export for that locale.
    settings.TBX_TITLE = "Sample Title"
    settings.TBX_DESCRIPTION = "Sample Description"
    term = make_term(1, "Sample Term", None)
    term.filtered_translations = []

    result = "".join(build_tbx_file([term], "fr-FR"))

    root = ET.fromstring(result)
    assert find_all(root, "term") == []
