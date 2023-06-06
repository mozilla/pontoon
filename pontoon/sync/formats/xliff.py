"""
Parser for the xliff translation format.
"""
from lxml import etree
from translate.storage import xliff
import copy

from pontoon.sync.exceptions import ParseError
from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.vcs.models import VCSTranslation


class XLIFFEntity(VCSTranslation):
    """
    Interface for modifying a single entity in an xliff file.
    """
    # OLD CODE
    # def __init__(self, order, unit):
    #     self.order = order
    #     self.unit = unit
    #     self.strings = {None: self.target_string} if self.target_string else {}

    def __init__(
        self,
        key,
        source_string,
        source_string_plural,
        strings,
        comments=None,
        order=None,
        unit=None
    ):
        super().__init__(
            key=key,
            context=key,
            source_string=source_string,
            source_string_plural=source_string_plural,
            strings=strings,
            comments=comments or [],
            fuzzy=False,
            order=order,
        )
        self.unit = unit

    def __repr__(self):
        return "<XLIFFEntity {key}>".format(key=self.key)

    # @property
    # def key(self):
    #     return self.unit.getid()

    # @property
    # def context(self):
    #     return self.unit.xmlelement.get("id") or ""

    # @property
    # def source_string(self):
    #     return str(self.unit.rich_source[0])

    # @property
    # def source_string_plural(self):
    #     return ""

    # @property
    # def comments(self):
    #     notes = self.unit.getnotes()
    #     return notes.split("\n") if notes else []

    # @property
    # def fuzzy(self):
    #     return False

    # @fuzzy.setter
    # def fuzzy(self, fuzzy):
    #     pass  # We don't use fuzzy in XLIFF

    # @property
    # def source(self):
    #     return []

    # @property
    # def target_string(self):
    #     return str(self.unit.get_rich_target()[0])

    # @target_string.setter
    # def target_string(self, value):
    #     self.unit.settarget(value)

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
    def __init__(self, path, locale, source_resource=None):
        self.path = path
        self.locale = locale
        self.source_resource = source_resource
        self.entities = {}

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = XLIFFEntity(
                    entity.key,
                    "",
                    "",
                    {},
                    copy.copy(entity.comments),
                    entity.order,
                )

        # Open the file at the provided path
        with open(path) as f:
            # Read the contents of the file and encode it 
            xml = f.read().encode("utf-8")

            try:
                # Parse the xml content of the file into an XLIFF file object
                self.xliff_file = xliff.xlifffile(xml)
            except etree.XMLSyntaxError as err:
                # If there is an error parsing the file, raise a ParseError 
                raise ParseError(f"Failed to parse {path}: {err}")

            # Loop through each unit in the XLIFF file
            for order, unit in enumerate(self.xliff_file.units):
                # Get the unit's ID and source string
                key = unit.getid()
                source_string = unit.rich_source[0]
                source_string_plural = ""

                # Get the translated string for the unit. If there's no target string, this will be an empty dictionary
                target_string = unit.get_rich_target()[0] if unit.get_rich_target() else None
                strings = {None: target_string} if target_string else {}


                # Get the unit's comments, split by newline characters
                comments = unit.getnotes().split("\n") if unit.getnotes() else []

                # Create a new XLIFFEntity from the unit
                entity = XLIFFEntity(
                    key,
                    source_string,
                    source_string_plural,
                    strings,
                    comments,
                    order,
                    unit
                )
                print(f"Adding entity with key {entity.key} to entities")
                # Add the entity to the entities dictionary using its key as the dictionary key
                self.entities[entity.key] = entity


        # OLD CODE
        # self.path = path
        # self.xliff_file = xliff_file
        # self.entities = [
        #     XLIFFEntity(order, unit) for order, unit in enumerate(self.xliff_file.units)
        # ]

    @property
    def translations(self):
        return self.entities

    def save(self, locale):
        # for entity in self.entities:
        #     entity.sync_changes()

        # locale_code = locale.code

        # TODO: should be made iOS specific
        # Map locale codes for iOS: http://www.ibabbleon.com/iOS-Language-Codes-ISO-639.html
        locale_mapping = {
            "bn-IN": "bn",
            "ga-IE": "ga",
            "nb-NO": "nb",
            "nn-NO": "nn",
            "sv-SE": "sv",
        }
        locale_code = locale.code
        if locale_code in locale_mapping:
            locale_code = locale_mapping[locale_code]

        # Set target-language if not set
        file_node = self.xliff_file.namespaced("file")
        for node in self.xliff_file.document.getroot().iterchildren(file_node):
            if not node.get("target-language"):
                node.set("target-language", locale_code)
        
        for entity in self.entities.values():
            entity.sync_changes()

        with open(self.path, "wb") as f:
            f.write(bytes(self.xliff_file))
        
        return

# OLD PARSE FUNCTION
# def parse(path, source_path=None, locale=None):
#     with open(path) as f:
#         xml = f.read().encode("utf-8")

#         try:
#             xliff_file = xliff.xlifffile(xml)
#         except etree.XMLSyntaxError as err:
#             raise ParseError(f"Failed to parse {path}: {err}")

#     return XLIFFResource(path, xliff_file)

def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = XLIFFResource(source_path, locale)
    else:
        source_resource = None

    return XLIFFResource(path, locale, source_resource)