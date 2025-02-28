"""
Parser for the strings.xml file format.
"""

import logging

from collections import OrderedDict

from compare_locales import parser

from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.formats.exceptions import ParseError
from pontoon.sync.vcs.translation import VCSTranslation


log = logging.getLogger(__name__)


class XMLEntity(VCSTranslation):
    """
    Represents an entity in an XML file.
    """

    def __init__(self, key, string, comment, order):
        self.key = key
        self.context = key
        self.source_string = string
        self.source_string_plural = ""
        self.strings = (
            {None: self.source_string} if self.source_string is not None else {}
        )
        self.comments = comment.val.split("\n") if comment else []
        self.order = order
        self.fuzzy = False
        self.source = []


class XMLResource(ParsedResource):
    def __init__(self, path, source_resource=None):
        self.path = path
        self.entities = OrderedDict()  # Preserve entity order.

        try:
            self.parser = parser.getParser(self.path)
        except UserWarning as err:
            raise ParseError(err)

        # A monolingual l10n file might not contain all entities, but the code
        # expects ParsedResource to contain representations of all of them. So
        # when parsing the l10n resource, we first create empty entity for each
        # source resource entity.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = XMLEntity(
                    entity.key,
                    None,
                    None,
                    0,
                )

        try:
            self.parser.readFile(self.path)
        except OSError as err:
            # If the file doesn't exist, but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        order = 0
        for entity in self.parser.walk():
            if isinstance(entity, parser.Entity):
                self.entities[entity.key] = XMLEntity(
                    entity.key,
                    entity.unwrap().replace("\\'", "'"),
                    entity.pre_comment,
                    order,
                )
                order += 1

    @property
    def translations(self):
        return sorted(self.entities.values(), key=lambda e: e.order)


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = XMLResource(source_path)
    else:
        source_resource = None

    return XMLResource(path, source_resource)
