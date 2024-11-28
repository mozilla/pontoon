from xml.sax.saxutils import escape, quoteattr

from django.conf import settings


def build_tbx_v2_file(term_translations, locale):
    """
    Generates contents of the TBX 2008 (v2) file (TBX-Default dialect):

    TBX files could contain large amount of entries and it's impossible to render all the data with
    django templates. Rendering a string in memory is a lot faster.
    """
    # Header
    yield f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE martif SYSTEM "TBXcoreStructV02.dtd">
<martif type="TBX" xml:lang="en-US">
    <martifHeader>
        <fileDesc>
            <titleStmt>
                <title>{escape(settings.TBX_TITLE)}</title>
            </titleStmt>
            <sourceDesc>
                <p>{escape(settings.TBX_DESCRIPTION)}</p>
            </sourceDesc>
        </fileDesc>
        <encodingDesc>
            <p type="XCSURI">TBXXCSV02.xcs</p>
        </encodingDesc>
    </martifHeader>
    <text>
        <body>"""

    # Body
    for translation in term_translations:
        term = translation.term
        yield f"""
            <termEntry id="c{term.pk}">
                <descrip type="context">{escape(term.usage)}</descrip>
                <langSet xml:lang="en-US">
                    <ntig>
                        <termGrp>
                            <term>{escape(term.text)}</term>
                            <termNote type="partOfSpeech">{escape(term.part_of_speech)}</termNote>
                        </termGrp>
                    </ntig>
                    <descripGrp>
                        <descrip type="definition">{escape(term.definition)}</descrip>
                    </descripGrp>
                </langSet>
                <langSet xml:lang={quoteattr(locale)}>
                    <ntig>
                        <termGrp>
                            <term>{escape(translation.text)}</term>
                        </termGrp>
                    </ntig>
                </langSet>
            </termEntry>"""

    # Footer
    yield """
        </body>
    </text>
</martif>
"""


def build_tbx_v3_file(term_translations, locale):
    """
    Generates contents of the TBX v3 file (TBX-Basic dialect, DCT style):

    TBX files could contain large amount of entries and it's impossible to render all the data with
    django templates. Rendering a string in memory is a lot faster.
    """
    # Header
    yield f"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="https://raw.githubusercontent.com/LTAC-Global/TBX-Basic_dialect/master/DCA/TBXcoreStructV03_TBX-Basic_integrated.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="https://raw.githubusercontent.com/LTAC-Global/TBX-Basic_dialect/master/DCA/TBX-Basic_DCA.sch" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>
<tbx style="dca" type="TBX-Basic" xml:lang="en" xmlns="urn:iso:std:iso:30042:ed-2">
    <tbxHeader>
        <fileDesc>
            <titleStmt>
                <title>{escape(settings.TBX_TITLE)}</title>
            </titleStmt>
            <sourceDesc>
                <p>{escape(settings.TBX_DESCRIPTION)}</p>
            </sourceDesc>
        </fileDesc>
        <encodingDesc>
            <p type="XCSURI">TBXXCSV02.xcs</p>
        </encodingDesc>
    </tbxHeader>
    <text>
        <body>"""

    # Body
    for translation in term_translations:
        term = translation.term
        yield f"""
            <conceptEntry id="c{term.pk}">
                <langSec xml:lang="en-US">
                    <termSec>
                        <term>{escape(term.text)}</term>
                        <termNote type="partOfSpeech">{escape(term.part_of_speech)}</termNote>
                        <descripGrp>
                            <descrip type="definition">{escape(term.definition)}</descrip>
                            <descrip type="context">{escape(term.usage)}</descrip>
                        </descripGrp>
                    </termSec>
                </langSec>
                <langSec xml:lang={quoteattr(locale)}>
                    <termSec>
                        <term>{escape(translation.text)}</term>
                    </termSec>
                </langSec>
            </conceptEntry>"""

    # Footer
    yield """
        </body>
    </text>
</tbx>
"""
