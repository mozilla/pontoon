from __future__ import absolute_import

import codecs
import copy
import logging
import os

from ftl.format.parser import FTLParser, ParseContext, L10nError
from ftl.format.serializer import FTLSerializer

from pontoon.sync import SyncError
from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.vcs.models import VCSTranslation

log = logging.getLogger(__name__)


class L20NEntity(VCSTranslation):
    """
    Represents entities in l20n (without its attributes).
    """
    def __init__(self, key, source_string, source_string_plural, strings, comments=None, order=None):
        super(L20NEntity, self).__init__(
            key=key,
            source_string=source_string,
            source_string_plural=source_string_plural,
            strings=strings,
            comments=comments or [],
            fuzzy=False,
            order=order,
        )

    def __repr__(self):
        return '<L20NEntity {key}>'.format(key=self.key.encode('utf-8'))


class L20NResource(ParsedResource):
    def __init__(self, path, locale, source_resource=None):
        self.path = path
        self.locale = locale
        self.entities = {}
        self.source_resource = source_resource
        self.order = 0

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = L20NEntity(
                    entity.key,
                    '',
                    '',
                    {},
                    copy.copy(entity.comments),
                    entity.order
                )

        try:
            with codecs.open(path, 'r', 'utf-8') as resource:
                self.structure = FTLParser().parseResource(resource.read())
        except IOError:
            # If the file doesn't exist, but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise

        def get_comment(obj):
            return [obj['comment']['content']] if obj['comment'] else []

        def parse_entity(obj, section_comment=[]):
            translation = FTLSerializer().dumpEntity(obj).split('=', 1)[1].lstrip(' ')
            self.entities[obj['id']['name']] = L20NEntity(
                obj['id']['name'],
                translation,
                '',
                {None: translation},
                section_comment + get_comment(obj),
                self.order
            )
            self.order += 1

        for obj in self.structure[0]['body']:
            if obj['type'] == 'Entity':
                parse_entity(obj)

            elif obj['type'] == 'Section':
                section_comment = get_comment(obj)
                for obj in obj['body']:
                    if obj['type'] == 'Entity':
                        parse_entity(obj, section_comment)

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
            raise SyncError('Cannot save l20n resource {0}: No source resource given.'
                            .format(self.path))

        with codecs.open(self.source_resource.path, 'r', 'utf-8') as resource:
            structure = FTLParser().parseResource(resource.read())

        def serialize_entity(obj, entities):
            entity_id = obj['id']['name']
            translations = self.entities[entity_id].strings

            if translations:
                source = translations[None]
                key = self.entities[entity_id].key

		# TODO: Make serialization less fragile
                try:
                    entity = ParseContext(key + '=' + source).getEntity().toJSON()
                except L10nError:
                    log.info('FTL serialization erorr in file {0}, locale {1}, key {2}'.format(self.path, self.locale, key))
                    raise

                obj['value'] = entity['value']
                obj['traits'] = entity['traits']
            else:
                index = entities.index(obj)
                del entities[index]

        entities = structure[0]['body']

        # Use list() to iterate over a copy, leaving original free to modify
        for obj in list(entities):
            if obj['type'] == 'Entity':
                serialize_entity(obj, entities)

            elif obj['type'] == 'Section':
                index = entities.index(obj)
                section = entities[index]['body']

                for obj in list(section):
                    if obj['type'] == 'Entity':
                        serialize_entity(obj, section)

                # Remove section if empty
                if len(section) == 0:
                    del entities[index]

        # Create parent directory if it doesn't exist.
        try:
            os.makedirs(os.path.dirname(self.path))
        except OSError:
            pass  # Already exists, phew!

        with codecs.open(self.path, 'w+', 'utf-8') as f:
            f.write(FTLSerializer().serialize(structure[0]))
            log.debug('Saved file: %s', self.path)


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = L20NResource(source_path, locale)
    else:
        source_resource = None
    return L20NResource(path, locale, source_resource)
