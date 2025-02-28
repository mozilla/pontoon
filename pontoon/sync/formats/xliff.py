"""
Parser for the xliff translation format.
"""

import copy

from lxml import etree

from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.formats.exceptions import ParseError
from pontoon.sync.vcs.translation import VCSTranslation
from translate.storage import xliff


class XLIFFEntity(VCSTranslation):
    """
    Interface for modifying a single entity in an xliff file.
    """

    def __init__(
        self,
        key,
        context,
        source_string,
        source_string_plural,
        strings,
        comments=None,
        order=None,
    ):
        super().__init__(
            key=key,
            context=context,
            source_string=source_string,
            source_string_plural=source_string_plural,
            strings=strings,
            comments=comments or [],
            fuzzy=False,
            order=order,
        )

    def __repr__(self):
        return f"<XLIFFEntity {self.key}>"


class XLIFFResource(ParsedResource):
    def __init__(self, path, locale, source_resource=None):
        self.path = path
        self.locale = locale
        self.entities = {}

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = XLIFFEntity(
                    entity.key, "", "", "", {}, copy.copy(entity.comments), entity.order
                )

        # Open the file at the provided path
        with open(path) as f:
            # Read the contents of the file and encode it
            xml = f.read().encode("utf-8")

            try:
                # Parse the xml content of the file into an XLIFF file object
                xliff_file = xliff.xlifffile(xml)
            except etree.XMLSyntaxError as err:
                # If there is an error parsing the file, raise a ParseError
                raise ParseError(f"Failed to parse {path}: {err}")

            # Loop through each unit in the XLIFF file
            for order, unit in enumerate(xliff_file.units):
                # Get the unit's ID and source string
                key = unit.getid()
                context = unit.xmlelement.get("id")
                source_string = str(unit.rich_source[0])
                source_string_plural = ""

                # Get the translated string for the unit. If there's no target string, this will be an empty dictionary
                target_string = (
                    str(unit.get_rich_target()[0]) if unit.get_rich_target() else None
                )
                strings = {None: target_string} if target_string else {}

                # Get the unit's comments, split by newline characters
                comments = unit.getnotes().split("\n") if unit.getnotes() else []

                # Create a new XLIFFEntity from the unit
                entity = XLIFFEntity(
                    key,
                    context,
                    source_string,
                    source_string_plural,
                    strings,
                    comments,
                    order,
                )
                # Add the entity to the entities dictionary using its key as the dictionary key
                self.entities[entity.key] = entity

    @property
    def translations(self):
        return sorted(self.entities.values(), key=lambda e: e.order)


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = XLIFFResource(source_path, locale)
    else:
        source_resource = None

    return XLIFFResource(path, locale, source_resource)
