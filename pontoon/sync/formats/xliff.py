"""
Parser for the xliff translation format.
"""
from lxml import etree
from translate.storage import xliff

from pontoon.sync.exceptions import ParseError
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

    @property
    def key(self):
        return self.unit.getid()

    @property
    def context(self):
        return self.unit.xmlelement.get("id") or ""

    @property
    def source_string(self):
        return str(self.unit.rich_source[0])

    @property
    def source_string_plural(self):
        return ""

    @property
    def comments(self):
        notes = self.unit.getnotes()
        return notes.split("\n") if notes else []

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
        return str(self.unit.get_rich_target()[0])

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
            # Store updated nodes
            xml = self.unit.xmlelement
            target = xml.find(self.unit.namespaced("target"))

        else:
            # Read stored nodes
            xml = self.unit.xmlelement
            target = xml.find(self.unit.namespaced("target"))
            if target is not None:
                xml.remove(target)

        # Clear unused approved tag
        if "approved" in xml.attrib:
            del xml.attrib["approved"]

        # Clear unused state tag
        if target is not None and "state" in target.attrib:
            del target.attrib["state"]


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

        locale_code = locale.code

        # TODO: should be made iOS specific
        # Map locale codes for iOS: http://www.ibabbleon.com/iOS-Language-Codes-ISO-639.html
        locale_mapping = {
            "bn-IN": "bn",
            "ga-IE": "ga",
            "nb-NO": "nb",
            "nn-NO": "nn",
            "sv-SE": "sv",
        }

        if locale_code in locale_mapping:
            locale_code = locale_mapping[locale_code]

        # Set target-language if not set
        file_node = self.xliff_file.namespaced("file")
        for node in self.xliff_file.document.getroot().iterchildren(file_node):
            if not node.get("target-language"):
                node.set("target-language", locale_code)

        with open(self.path, "wb") as f:
            f.write(bytes(self.xliff_file))


def parse(path, source_path=None, locale=None):
    with open(path) as f:
        xml = f.read().encode("utf-8")

        try:
            xliff_file = xliff.xlifffile(xml)
        except etree.XMLSyntaxError as err:
            raise ParseError(f"Failed to parse {path}: {err}")

    return XLIFFResource(path, xliff_file)
