from __future__ import absolute_import

import codecs
import copy
import logging
import os

from fluent.syntax import (
    ast,
    FluentParser,
    FluentSerializer
)

from pontoon.sync import SyncError
from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.vcs.models import VCSTranslation

log = logging.getLogger(__name__)


parser = FluentParser()
serializer = FluentSerializer()

class FTLEntity(VCSTranslation):
    """
    Represents entities in FTL (without its attributes).
    """
    def __init__(self, key, source_string, source_string_plural, strings, comments=None, order=None):
        super(FTLEntity, self).__init__(
            key=key,
            source_string=source_string,
            source_string_plural=source_string_plural,
            strings=strings,
            comments=comments or [],
            fuzzy=False,
            order=order,
        )

    def __repr__(self):
        return '<FTLEntity {key}>'.format(key=self.key.encode('utf-8'))


class FTLResource(ParsedResource):
    def __init__(self, path, locale, source_resource=None):
        self.path = path
        self.locale = locale
        self.entities = {}
        self.source_resource = source_resource
        self.order = 0

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = FTLEntity(
                    entity.key,
                    '',
                    '',
                    {},
                    copy.copy(entity.comments),
                    entity.order
                )

        try:
            with codecs.open(path, 'r', 'utf-8') as resource:
                self.structure = parser.parse(resource.read())
        except IOError:
            # If the file doesn't exist, but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise

        def get_comment(obj):
            return [obj.comment.content] if obj.comment else []

        section_comment = None
        for obj in self.structure.body:
            if type(obj) == ast.Message:
                key = obj.id.name
                translation = serializer.serialize_entry(obj)

                # If syncing locale file
                if source_resource:
                    split = translation.split('\n' + key + ' = ')
                    if len(split) > 1:
                        serialized_comment = split[0] + '\n'
                        translation = translation[len(serialized_comment):]

                self.entities[key] = FTLEntity(
                    key,
                    translation,
                    '',
                    {None: translation},
                    (section_comment or []) + get_comment(obj),
                    self.order
                )
                self.order += 1

            elif type(obj) == ast.Section:
                section_comment = get_comment(obj)

    @property
    def translations(self):
        return sorted(self.entities.values(), key=lambda e: e.order)

    def save(self, locale):
        """
        Load the source resource, modify it with changes made to this
        Resource instance, and save it over the locale-specific
        resource.
        """
        if not self.source_resource:
            raise SyncError('Cannot save FTL resource {0}: No source resource given.'
                            .format(self.path))

        with codecs.open(self.source_resource.path, 'r', 'utf-8') as resource:
            structure = parser.parse(resource.read())

        entities = structure.body

        # Use list() to iterate over a copy, leaving original free to modify
        for obj in list(entities):
            if type(obj) == ast.Message:
                index = entities.index(obj)
                entity = self.entities[obj.id.name]

                if entity.strings:
                    message = parser.parse_entry(entity.strings[None])
                    message.comment = obj.comment
                    entities[index] = message
                else:
                    del entities[index]

        # Create parent directory if it doesn't exist.
        try:
            os.makedirs(os.path.dirname(self.path))
        except OSError:
            pass  # Already exists, phew!

        with codecs.open(self.path, 'w+', 'utf-8') as f:
            f.write(serializer.serialize(structure))
            log.debug('Saved file: %s', self.path)


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = FTLResource(source_path, locale)
    else:
        source_resource = None
    return FTLResource(path, locale, source_resource)
