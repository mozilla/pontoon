"""
Parser for the xliff translation format.
"""
from translate.storage import xliff

from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.vcs.models import VCSTranslation


class XLIFFEntity(VCSTranslation):
    """
    Interface for modifying a single entity in an xliff file.
    """
    def __init__(self, order, unit):
        self.order = order
        self.unit = unit
        self.strings = {None: self.target_string} if self.target_string else {}
        self.last_translator = None
        self.last_update = None

    @property
    def key(self):
        return self.unit.getid()

    @property
    def source_string(self):
        return unicode(self.unit.get_rich_source()[0])

    @property
    def source_string_plural(self):
        return ''

    @property
    def comments(self):
        notes = self.unit.getnotes()
        return notes.split('\n') if notes else []

    @property
    def fuzzy(self):
        return False

    @fuzzy.setter
    def fuzzy(self, fuzzy):
        pass  # We don't use fuzzy in XLIFF

    @property
    def source(self):
        return []

    @property
    def target_string(self):
        return unicode(self.unit.get_rich_target()[0])

    @target_string.setter
    def target_string(self, value):
        self.unit.settarget(value)

    def sync_changes(self):
        """
        Apply any changes made to this object to the backing unit in the
        xliff file.
        """
        if None in self.strings:
            self.target_string = self.strings[None]
        else:
            xml = self.unit.xmlelement

            if 'approved' in xml.attrib:
                del xml.attrib['approved']

            target = xml.find(self.unit.namespaced('target'))
            if target is not None:
                xml.remove(target)


class XLIFFResource(ParsedResource):
    def __init__(self, path, xliff_file):
        self.path = path
        self.xliff_file = xliff_file
        self.entities = [
            XLIFFEntity(order, unit) for order, unit in enumerate(self.xliff_file.units)
        ]

    @property
    def translations(self):
        return self.entities

    def save(self, locale):
        for entity in self.entities:
            entity.sync_changes()

        # Update target-language where necessary.
        file_node = self.xliff_file.namespaced('file')
        for node in self.xliff_file.document.getroot().iterchildren(file_node):
            node.set('target-language', locale.code)

        with open(self.path, 'w') as f:
            f.writelines(str(self.xliff_file))


def parse(path, source_path=None, locale=None):
    with open(path) as f:
        xliff_file = xliff.xlifffile(f)
    return XLIFFResource(path, xliff_file)
