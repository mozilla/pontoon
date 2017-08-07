"""
This module tries to implement subset of The TBX Basic format.

First version of the implementation allows to import terminology from The Microsoft Language Portal.
However, there's a lot corner-cases that aren't handled and they will be implemented in the future versions.
As the name suggest, TBX is the xml compliant format, that can be parsed by any xml library.
We try to wrap all xml structures in python classes to make the code more readable.
"""
from collections import namedtuple

from defusedxml.minidom import parseString


class MissingSourceTerm(Exception):
    """
    When Term doesn't contain Language translation for en-GB or en-US.
    """


class XMLObject(object):
    """
    All tbx objects will share the same constructor that will receive an instance of a xml object.
    """
    def __init__(self, xml_node):
        self.xml_node = xml_node

    @property
    def description(self):
        """
        Most of the object in tbx file have a description.
        """
        for child in self.xml_node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                continue

            if child.tagName == 'descrip':
                try:
                    return child.childNodes[0].data
                except IndexError:
                    return ''

            elif child.tagName == 'descripGrp':
                return child.childNodes[0].childNodes[0].data


class Translation(XMLObject):
    """
    Translation of term to a given language. Also contains information about the part of speech.
    """
    @property
    def text(self):
        try:
            return self.xml_node.getElementsByTagName('term')[0].childNodes[0].data
        except IndexError:
            return ''

    @property
    def notes(self):
        notes_ = {}
        for note in self.xml_node.getElementsByTagName('termNote'):
            note_type = str(note.getAttribute('type'))
            note_text = str(note.childNodes[0].data)

            notes_[note_type] = note_text
        return notes_

    @property
    def term_type(self):
        return self.notes.get('type')

    @property
    def part_of_speech(self):
        return self.notes.get('partOfSpeech')


class Language(XMLObject):
    """
    Mandatory section of TBX format. Stores translations of a term.
    """
    @property
    def lang(self):
        return self.xml_node.getAttribute('xml:lang')

    @property
    def translations(self):
        elements = self.xml_node.getElementsByTagName('ntig')

        if not elements.length:
            elements = self.xml_node.getElementsByTagName('tig')

        if not elements.length:
            return []
        return map(Translation, elements)


class XMLTerm(XMLObject):
    """
    It describes a term on The Conceptual level. In files provided by Microsoft, this is container for a single term
    and doesn't contain any top-level information, all data is stored in specific language sets.
    """
    @property
    def id(self):
        return self.xml_node.getAttribute('id')

    @property
    def languages(self):
        """
        A map of locale codes to their respective langset objects.
        """
        results = {}
        for lang_set in map(Language, self.xml_node.getElementsByTagName('langSet')):
            results[lang_set.lang] = lang_set
        return results

    @property
    def source_language(self):
        """
        Most of the code/structure in pontoon assume that base source strings are in en-GB or en-US.
        That implies that we'll need strings from these locales to perform join between existing entities and terms
        from the new terminology module.
        """
        lang = self.languages.get('en-US')
        if not lang:
            raise MissingSourceTerm()

        return lang

    @property
    def source_term(self):
        return self.source_language.translations[0]

    @property
    def source_text(self):
        return self.source_term.text

    @property
    def part_of_speech(self):
        return self.source_term.part_of_speech

    @property
    def description(self):
        return self.source_term.description or self.source_language.description

    @property
    def translations(self):
        trans = {}
        for lang_code, lang in self.languages.items():
            if lang_code == 'en-US':
                continue

            for term in lang.translations:
                if term.text:
                    trans.setdefault(lang.lang, []).append(term.text)

        return trans


# TbxTerm represents a small tuple which is easier to serialize, which is useful if you e.g.
# try a parallel import of terms from a terminology file.

TbxTerm = namedtuple('TbxTerm', (
    'term_id',
    'source_text',
    'part_of_speech',
    'description',
    'translations'
))


def parse_terms(file_contents):
    """
    Parse a TBX file and return possiby all terms that are inside.

    :param str file_contents: contents of a tbx file
    :returns: a list of VCSTerm complaint objects
    """
    xml_file = parseString(file_contents)
    tbx_terms = []
    for entryTerm in xml_file.getElementsByTagName('termEntry'):
        xml_term = XMLTerm(entryTerm)
        tbx_terms.append(
            TbxTerm(
                xml_term.id,
                xml_term.source_text,
                xml_term.part_of_speech or '',
                xml_term.description or '',
                xml_term.translations
            )
        )
    return tbx_terms
