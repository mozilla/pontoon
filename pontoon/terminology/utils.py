from xml.sax.saxutils import escape, quoteattr


def build_tbx_v2_file(term_translations, locale):
    """
    Generates contents of the TBX 2008 (v2) file (TBX-Default dialect):

    TBX files could contain large amount of entries and it's impossible to render all the data with
    django templates. Rendering a string in memory is a lot faster.
    """
    yield (
        u'<?xml version="1.0" encoding="UTF-8"?>'
        u'\n<!DOCTYPE martif SYSTEM "TBXcoreStructV02.dtd">'
        u'\n<martif type="TBX" xml:lang="en-US">'
        u"\n\t<martifHeader>"
        u"\n\t\t<fileDesc>"
        u"\n\t\t\t<titleStmt>"
        u"\n\t\t\t\t<title>Mozilla Terms</title>"
        u"\n\t\t\t</titleStmt>"
        u"\n\t\t\t<sourceDesc>"
        u"\n\t\t\t\t<p>from a Mozilla termbase</p>"
        u"\n\t\t\t</sourceDesc>"
        u"\n\t\t</fileDesc>"
        u"\n\t\t<encodingDesc>"
        u'\n\t\t\t<p type="XCSURI">TBXXCSV02.xcs</p>'
        u"\n\t\t</encodingDesc>"
        u"\n\t</martifHeader>"
        u"\n\t<text>"
        u"\n\t\t<body>"
    )

    for translation in term_translations:
        term = translation.term
        yield (
            u'\n\t\t\t<termEntry id="c%(id)s">'
            u'\n\t\t\t\t<descrip type="context">%(usage)s</descrip>'
            u'\n\t\t\t\t<langSet xml:lang="en-US">'
            u"\n\t\t\t\t\t<ntig>"
            u"\n\t\t\t\t\t\t<termGrp>"
            u"\n\t\t\t\t\t\t\t<term>%(term)s</term>"
            u'\n\t\t\t\t\t\t\t<termNote type="partOfSpeech">%(part_of_speech)s</termNote>'
            u"\n\t\t\t\t\t\t</termGrp>"
            u"\n\t\t\t\t\t</ntig>"
            u"\n\t\t\t\t\t<descripGrp>"
            u'\n\t\t\t\t\t\t<descrip type="definition">%(definition)s</descrip>'
            u"\n\t\t\t\t\t</descripGrp>"
            u"\n\t\t\t\t</langSet>"
            u"\n\t\t\t\t<langSet xml:lang=%(locale)s>"
            u"\n\t\t\t\t\t<ntig>"
            u"\n\t\t\t\t\t\t<termGrp>"
            u"\n\t\t\t\t\t\t\t<term>%(translation)s</term>"
            u"\n\t\t\t\t\t\t</termGrp>"
            u"\n\t\t\t\t\t</ntig>"
            u"\n\t\t\t\t</langSet>"
            u"\n\t\t\t</termEntry>"
            % {
                "id": term.pk,
                "term": escape(term.text),
                "part_of_speech": escape(term.part_of_speech),
                "definition": escape(term.definition),
                "usage": escape(term.usage),
                "locale": quoteattr(locale),
                "translation": escape(translation.text),
            }
        )

    yield (u"\n\t\t</body>" u"\n\t</text>" u"\n</martif>\n")


def build_tbx_v3_file(term_translations, locale):
    """
    Generates contents of the TBX v3 file (TBX-Basic dialect, DCT style):

    TBX files could contain large amount of entries and it's impossible to render all the data with
    django templates. Rendering a string in memory is a lot faster.
    """
    yield (
        u'<?xml version="1.0" encoding="UTF-8"?>'
        u'\n<?xml-model href="https://raw.githubusercontent.com/LTAC-Global/TBX-Basic_dialect/master/DCA/TBXcoreStructV03_TBX-Basic_integrated.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>'
        u'\n<?xml-model href="https://raw.githubusercontent.com/LTAC-Global/TBX-Basic_dialect/master/DCA/TBX-Basic_DCA.sch" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>'
        u'\n<tbx style="dca" type="TBX-Basic" xml:lang="en" xmlns="urn:iso:std:iso:30042:ed-2">'
        u"\n\t<tbxHeader>"
        u"\n\t\t<fileDesc>"
        u"\n\t\t\t<titleStmt>"
        u"\n\t\t\t\t<title>Mozilla Terms</title>"
        u"\n\t\t\t</titleStmt>"
        u"\n\t\t\t<sourceDesc>"
        u"\n\t\t\t\t<p>from a Mozilla termbase</p>"
        u"\n\t\t\t</sourceDesc>"
        u"\n\t\t</fileDesc>"
        u"\n\t\t<encodingDesc>"
        u'\n\t\t\t<p type="XCSURI">TBXXCSV02.xcs</p>'
        u"\n\t\t</encodingDesc>"
        u"\n\t</tbxHeader>"
        u"\n\t<text>"
        u"\n\t\t<body>"
    )

    for translation in term_translations:
        term = translation.term
        yield (
            u'\n\t\t\t<conceptEntry id="c%(id)s">'
            u'\n\t\t\t\t<langSec xml:lang="en-US">'
            u"\n\t\t\t\t\t<termSec>"
            u"\n\t\t\t\t\t\t<term>%(term)s</term>"
            u'\n\t\t\t\t\t\t<termNote type="partOfSpeech">%(part_of_speech)s</termNote>'
            u"\n\t\t\t\t\t\t<descripGrp>"
            u'\n\t\t\t\t\t\t\t<descrip type="definition">%(definition)s</descrip>'
            u'\n\t\t\t\t\t\t\t<descrip type="context">%(usage)s</descrip>'
            u"\n\t\t\t\t\t\t</descripGrp>"
            u"\n\t\t\t\t\t</termSec>"
            u"\n\t\t\t\t</langSec>"
            u"\n\t\t\t\t<langSec xml:lang=%(locale)s>"
            u"\n\t\t\t\t\t<termSec>"
            u"\n\t\t\t\t\t\t<term>%(translation)s</term>"
            u"\n\t\t\t\t\t</termSec>"
            u"\n\t\t\t\t</langSec>"
            u"\n\t\t\t</conceptEntry>"
            % {
                "id": term.pk,
                "term": escape(term.text),
                "part_of_speech": escape(term.part_of_speech),
                "definition": escape(term.definition),
                "usage": escape(term.usage),
                "locale": quoteattr(locale),
                "translation": escape(translation.text),
            }
        )

    yield (u"\n\t\t</body>" u"\n\t</text>" u"\n</tbx>\n")
