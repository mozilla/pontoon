from xml.sax.saxutils import escape, quoteattr


def build_tbx_v2_file(term_translations, locale):
    """
    Generates contents of the TBX 2008 (v2) file (TBX-Default dialect):

    TBX files could contain large amount of entries and it's impossible to render all the data with
    django templates. Rendering a string in memory is a lot faster.
    """
    yield (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '\n<!DOCTYPE martif SYSTEM "TBXcoreStructV02.dtd">'
        '\n<martif type="TBX" xml:lang="en-US">'
        "\n\t<martifHeader>"
        "\n\t\t<fileDesc>"
        "\n\t\t\t<titleStmt>"
        "\n\t\t\t\t<title>Mozilla Terms</title>"
        "\n\t\t\t</titleStmt>"
        "\n\t\t\t<sourceDesc>"
        "\n\t\t\t\t<p>from a Mozilla termbase</p>"
        "\n\t\t\t</sourceDesc>"
        "\n\t\t</fileDesc>"
        "\n\t\t<encodingDesc>"
        '\n\t\t\t<p type="XCSURI">TBXXCSV02.xcs</p>'
        "\n\t\t</encodingDesc>"
        "\n\t</martifHeader>"
        "\n\t<text>"
        "\n\t\t<body>"
    )

    for translation in term_translations:
        term = translation.term
        yield (
            '\n\t\t\t<termEntry id="c%(id)s">'
            '\n\t\t\t\t<descrip type="context">%(usage)s</descrip>'
            '\n\t\t\t\t<langSet xml:lang="en-US">'
            "\n\t\t\t\t\t<ntig>"
            "\n\t\t\t\t\t\t<termGrp>"
            "\n\t\t\t\t\t\t\t<term>%(term)s</term>"
            '\n\t\t\t\t\t\t\t<termNote type="partOfSpeech">%(part_of_speech)s</termNote>'
            "\n\t\t\t\t\t\t</termGrp>"
            "\n\t\t\t\t\t</ntig>"
            "\n\t\t\t\t\t<descripGrp>"
            '\n\t\t\t\t\t\t<descrip type="definition">%(definition)s</descrip>'
            "\n\t\t\t\t\t</descripGrp>"
            "\n\t\t\t\t</langSet>"
            "\n\t\t\t\t<langSet xml:lang=%(locale)s>"
            "\n\t\t\t\t\t<ntig>"
            "\n\t\t\t\t\t\t<termGrp>"
            "\n\t\t\t\t\t\t\t<term>%(translation)s</term>"
            "\n\t\t\t\t\t\t</termGrp>"
            "\n\t\t\t\t\t</ntig>"
            "\n\t\t\t\t</langSet>"
            "\n\t\t\t</termEntry>"
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

    yield ("\n\t\t</body>" "\n\t</text>" "\n</martif>\n")


def build_tbx_v3_file(term_translations, locale):
    """
    Generates contents of the TBX v3 file (TBX-Basic dialect, DCT style):

    TBX files could contain large amount of entries and it's impossible to render all the data with
    django templates. Rendering a string in memory is a lot faster.
    """
    yield (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '\n<?xml-model href="https://raw.githubusercontent.com/LTAC-Global/TBX-Basic_dialect/master/DCA/TBXcoreStructV03_TBX-Basic_integrated.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>'
        '\n<?xml-model href="https://raw.githubusercontent.com/LTAC-Global/TBX-Basic_dialect/master/DCA/TBX-Basic_DCA.sch" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>'
        '\n<tbx style="dca" type="TBX-Basic" xml:lang="en" xmlns="urn:iso:std:iso:30042:ed-2">'
        "\n\t<tbxHeader>"
        "\n\t\t<fileDesc>"
        "\n\t\t\t<titleStmt>"
        "\n\t\t\t\t<title>Mozilla Terms</title>"
        "\n\t\t\t</titleStmt>"
        "\n\t\t\t<sourceDesc>"
        "\n\t\t\t\t<p>from a Mozilla termbase</p>"
        "\n\t\t\t</sourceDesc>"
        "\n\t\t</fileDesc>"
        "\n\t\t<encodingDesc>"
        '\n\t\t\t<p type="XCSURI">TBXXCSV02.xcs</p>'
        "\n\t\t</encodingDesc>"
        "\n\t</tbxHeader>"
        "\n\t<text>"
        "\n\t\t<body>"
    )

    for translation in term_translations:
        term = translation.term
        yield (
            '\n\t\t\t<conceptEntry id="c%(id)s">'
            '\n\t\t\t\t<langSec xml:lang="en-US">'
            "\n\t\t\t\t\t<termSec>"
            "\n\t\t\t\t\t\t<term>%(term)s</term>"
            '\n\t\t\t\t\t\t<termNote type="partOfSpeech">%(part_of_speech)s</termNote>'
            "\n\t\t\t\t\t\t<descripGrp>"
            '\n\t\t\t\t\t\t\t<descrip type="definition">%(definition)s</descrip>'
            '\n\t\t\t\t\t\t\t<descrip type="context">%(usage)s</descrip>'
            "\n\t\t\t\t\t\t</descripGrp>"
            "\n\t\t\t\t\t</termSec>"
            "\n\t\t\t\t</langSec>"
            "\n\t\t\t\t<langSec xml:lang=%(locale)s>"
            "\n\t\t\t\t\t<termSec>"
            "\n\t\t\t\t\t\t<term>%(translation)s</term>"
            "\n\t\t\t\t\t</termSec>"
            "\n\t\t\t\t</langSec>"
            "\n\t\t\t</conceptEntry>"
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

    yield ("\n\t\t</body>" "\n\t</text>" "\n</tbx>\n")
