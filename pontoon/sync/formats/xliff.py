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
        # print(f"Unit: {unit}, ID: {unit.getid()}")  # Add this line
        self.strings = {None: self.target_string} if self.target_string else {}
        # print(f"Initialized XLIFFEntity with key: {self.key}")
        # print(f"Initialized XLIFFEntity with target string: {self.target_string}")


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
        # print(f"Set target string to: {value}")

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
    def __init__(self, path, xliff_file, reference_path=None):
        self.path = path
        self.xliff_file = xliff_file
        self.reference_path = reference_path
        self.entities = [
            XLIFFEntity(order, unit) for order, unit in enumerate(self.xliff_file.units)
        ]

    @property
    def translations(self):
        # print(f"XLIFFResource translations: {self.entities}")
        return self.entities
        

    def save(self, locale):
        """
        Load the reference XLIFF file, modify it with translations made to this 
        Resource instance, and save it over the locale-specific resource.
        """
        if self.reference_path is None:
            raise ValueError("reference_path cannot be None")
        
        for entity in self.entities:
            entity.sync_changes()

        # Load the reference XLIFF file
        with open(self.reference_path, 'r') as f:
            reference_xml = f.read().encode("utf-8")
            reference_xliff_file = xliff.xlifffile(reference_xml)

         # Update self.entities with new strings from the reference XLIFF file
        self.entities = [
            XLIFFEntity(order, unit) for order, unit in enumerate(reference_xliff_file.units)
        ]

        # Create a dictionary mapping keys to entities
        # entities_dict = {entity.key: entity for entity in self.entities}
        entities_dict = {entity.key.replace('\x04', ''): entity for entity in self.entities}
        
        # print(f"Keys in entities_dict: {entities_dict.keys()}")

        # Iterate over each unit in the reference XLIFF file
        for reference_unit in reference_xliff_file.units:
            reference_entity = XLIFFEntity(0, reference_unit)
            #If we have a translation for this entity, add it to the reference entity

            reference_entity_key = reference_entity.key.replace('\x04', '')
            if reference_entity_key in entities_dict: 
                entity = entities_dict[reference_entity_key]
                print(f"Entity strings: {entity.strings}")  # Print entity.strings

                if entity.strings and locale in entity.strings:
                    reference_entity.target_string = entity.strings[locale]
                    reference_entity.sync_changes()
              
                else: 
                    # If there is no translation, remove the target attribute
                    xml = reference_entity.unit.xmlelement
                    target = xml.find(reference_entity.unit.namespaced("target"))
                    if target is not None:
                        xml.remove(target)
        
        # Save the modified reference XLIFF file to the locale-specific resource
        with open(self.path, "wb") as f:
            f.write(bytes(reference_xliff_file))

        # for entity in self.entities:
        #     entity.sync_changes()

        # locale_code = locale.code

        # # TODO: should be made iOS specific
        # # Map locale codes for iOS: http://www.ibabbleon.com/iOS-Language-Codes-ISO-639.html
        # locale_mapping = {
        #     "bn-IN": "bn",
        #     "ga-IE": "ga",
        #     "nb-NO": "nb",
        #     "nn-NO": "nn",
        #     "sv-SE": "sv",
        # }

        # if locale_code in locale_mapping:
        #     locale_code = locale_mapping[locale_code]

        # # Set target-language if not set
        # file_node = self.xliff_file.namespaced("file")
        # for node in self.xliff_file.document.getroot().iterchildren(file_node):
        #     if not node.get("target-language"):
        #         node.set("target-language", locale_code)

        # with open(self.path, "wb") as f:
        #     f.write(bytes(self.xliff_file))


def parse(path, source_path=None, locale=None):
    with open(path) as f:
        xml = f.read().encode("utf-8")

        try:
            xliff_file = xliff.xlifffile(xml)
        except etree.XMLSyntaxError as err:
            raise ParseError(f"Failed to parse {path}: {err}")

    return XLIFFResource(path, xliff_file, source_path)
