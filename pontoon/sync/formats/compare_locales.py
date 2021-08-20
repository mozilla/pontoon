"""
Parser and serializer for file formats supported by compare-locales library:
https://hg.mozilla.org/l10n/compare-locales/
"""
import logging

from collections import OrderedDict
from compare_locales import (
    parser,
    serializer,
)

from pontoon.sync.exceptions import ParseError, SyncError
from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.utils import create_parent_directory
from pontoon.sync.vcs.models import VCSTranslation


log = logging.getLogger(__name__)


class CompareLocalesEntity(VCSTranslation):
    """
    Represents an entity in a file handled by compare-locales.
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


class CompareLocalesResource(ParsedResource):
    def __init__(self, path, source_resource=None):
        self.path = path
        self.entities = OrderedDict()  # Preserve entity order.
        self.source_resource = source_resource

        try:
            self.parser = parser.getParser(self.path)
        except UserWarning as err:
            raise ParseError(err)

        self.parsed_objects = []

        # A monolingual l10n file might not contain all entities, but the code
        # expects ParsedResource to contain representations of all of them. So
        # when parsing the l10n resource, we first create empty entity for each
        # source resource entity.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = CompareLocalesEntity(entity.key, None, None, 0,)

        try:
            self.parser.readFile(self.path)
        except OSError as err:
            # If the file doesn't exist, but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        self.parsed_objects = list(self.parser.walk())
        order = 0

        for entity in self.parsed_objects:
            if isinstance(entity, parser.Entity):
                self.entities[entity.key] = CompareLocalesEntity(
                    entity.key, entity.unwrap(), entity.pre_comment, order,
                )
                order += 1

    @property
    def translations(self):
        return sorted(self.entities.values(), key=lambda e: e.order)

    def save(self, locale):
        if not self.source_resource:
            raise SyncError(
                f"Cannot save resource {self.path}: No source resource given."
            )

        # A dictionary of new translations
        new_l10n = {
            key: entity.strings[None] if entity.strings else None
            for key, entity in self.entities.items()
        }

        # Create parent folders if necessary
        create_parent_directory(self.path)

        with open(self.path, "wb") as output_file:
            log.debug("Saving file: %s", self.path)
            output_file.write(
                serializer.serialize(
                    self.path,
                    self.source_resource.parsed_objects,
                    self.parsed_objects,
                    new_l10n,
                )
            )


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = CompareLocalesResource(source_path)
    else:
        source_resource = None

    return CompareLocalesResource(path, source_resource)
