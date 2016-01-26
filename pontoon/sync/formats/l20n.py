from __future__ import absolute_import

import codecs
import copy
import logging
import os

from l20n.format.parser import L20nParser
from l20n.format.serializer import Serializer
from l20n.format import ast

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

        with codecs.open(path, 'r', 'utf-8') as resource:
            self.structure = L20nParser().parse(resource.read())
            order = 0
            comments = []
            for obj in self.structure.body:
                if obj.type == 'Entity':
                    if obj.value and obj.value.type == 'String':
                        self.entities[obj.id.name] = L20NEntity(
                            obj.id.name,
                            obj.value.source,
                            '',
                            {None: obj.value.source},
                            comments,
                            order
                        )
                        order += 1

                    elif obj.value and obj.value.type == 'Hash':
                        strings = {
                            self.locale.get_plural_index(item.id.name):
                            item.value.source for item in obj.value.items
                        }
                        self.entities[obj.id.name] = L20NEntity(
                            obj.id.name,
                            strings.get(0, ''),
                            strings.get(1, ''),
                            strings,
                            comments,
                            order
                        )
                        order += 1

                    for attr in obj.attrs:
                        key = '.'.join([obj.id.name, attr.id.name])
                        self.entities[key] = L20NEntity(
                            key,
                            attr.value.source,
                            '',
                            {None: attr.value.source},
                            order=order
                        )
                        order += 1
                    comments = []

                elif obj.type == 'Comment':
                    comments.append(obj.body)

                else:
                    comments = []

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
            new_structure = L20nParser().parse(resource.read())

        def attr_key(entity, attr):
            """Returns key for the attributes of entity."""
            return '.'.join([entity.id.name, attr.id.name])

        to_remove = []
        for res_entity in new_structure.body:
            if res_entity.type == 'Entity':
                entity_id = res_entity.id.name
                translations = self.entities[entity_id].strings
                comments = self.entities[entity_id].comments

                if not translations:
                    entity_idx = new_structure.body.index(res_entity)

                    for comment_entity in new_structure.body[entity_idx-len(comments):entity_idx]:
                        to_remove.append((new_structure.body, comment_entity))

                    # Checks if any attribute contains translation, if not
                    # then we can remove wole entity.
                    has_attributes = any([
                        bool(self.entities[attr_key(res_entity, a)].strings)
                        for a in res_entity.attrs
                    ])

                    if has_attributes:
                        res_entity.value = None

                    else:
                        to_remove.append((new_structure.body, res_entity))
                        continue

                if res_entity.value and res_entity.value.type == 'String':
                    res_entity.value.content[0] = translations[None]

                elif res_entity.value and res_entity.value.type == 'Hash':
                    res_entity.value.items = [
                        ast.HashItem(
                            ast.Identifier(locale.get_relative_cldr_plural(plural_relative_id)),
                            ast.String([value], value),
                            False
                        ) for plural_relative_id, value in translations.items()]


                for attr in res_entity.attrs:
                    key = attr_key(res_entity, attr)
                    attr_translations = self.entities[key].strings
                    if not attr_translations:
                        to_remove.append((res_entity.attrs, attr))
                        continue
                    attr.value.content[0] = attr_translations[None]

        for parent, entity in to_remove:
            parent.remove(entity)

        # Create parent directory if it doesn't exist.
        try:
            os.makedirs(os.path.dirname(self.path))
        except OSError:
            pass  # Already exists, phew!

        with codecs.open(self.path, 'w+', 'utf-8') as f:
            f.write(Serializer().serialize(new_structure))
            log.debug("Saved file: %s", self.path)


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = L20NResource(source_path, locale)
    else:
        source_resource = None
    return L20NResource(path, locale, source_resource)
