"""
Parser and serializer for file formats supported by compare-locales library:
https://hg.mozilla.org/l10n/compare-locales/
"""
from __future__ import absolute_import

import logging

from collections import OrderedDict
from compare_locales import parser

from pontoon.sync.exceptions import ParseError
from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.vcs.models import VCSTranslation


log = logging.getLogger(__name__)


class CompareLocalesEntity(VCSTranslation):
    """
    Represents an entity in a file handled by compare-locales.
    """
    def __init__(self, key, string, comment, order):
        self.key = key
        self.source_string = string
        self.source_string_plural = ''
        self.strings = {None: self.source_string} if self.source_string is not None else {}
        self.comments = [c.strip() for c in comment.raw_val.split('\n')] if comment else []
        self.order = order
        self.fuzzy = False
        self.source = []


class CompareLocalesResource(ParsedResource):
    def __init__(self, path, source_resource=None):
        self.path = path
        self.entities = OrderedDict()  # Preserve entity order.
        self.source_resource = source_resource
        self.parser = parser.getParser(self.path)

        try:
            self.parser.readFile(self.path)
        except IOError as err:
            # If the file doesn't exist or cannot be decoded,
            # but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        entities = list(self.parser.parse())
        for order, entity in enumerate(entities):
            if isinstance(entity, parser.Entity):
                self.entities[entity.key] = CompareLocalesEntity(
                    entity.key,
                    entity.unwrap(),
                    entity.pre_comment,
                    order,
                )

    @property
    def translations(self):
        return sorted(self.entities.values(), key=lambda e: e.order)


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = CompareLocalesResource(source_path)
    else:
        source_resource = None

    return CompareLocalesResource(path, source_resource)
