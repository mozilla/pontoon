"""
Parser for key-value YAML, a nested Object structure of String values.
This implementation does not supports plurals.

Each key can be associated with either a String or an Object value.
Therefore, the format support nested values.

A key can contain any character.
Nested keys are internally stored as a YAML array.
"""
import os
from collections import OrderedDict
import yaml
import logging

from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.formats.exceptions import ParseError
from pontoon.sync.vcs.translation import VCSTranslation

log = logging.getLogger(__name__)

def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value

class YAMLKVEntity(VCSTranslation):
    """
    Represents an entity in a Key Value YAML file.
    """

    def __init__(self, order, key, source_value, value):
        super().__init__(
            order=order,
            key=key,
            context=key,
            source_string=source_value,
            strings={None: value}
            if value
            else {},  # No plural support in key value JSON
            comments=[],
            fuzzy=False,
        )

class YAMLResource(ParsedResource):
    def __init__(self, path, source_resource=None):
        self.path = path
        self.entities = OrderedDict()  # Preserve entity order.
        self.source_resource = source_resource

        file_exists = os.path.isfile(path)

        if not file_exists and not source_resource:
            raise ParseError("Can't have resources with no files or source resource.")

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = YAMLKVEntity(
                    entity.order, entity.key, "", ""
                )

        if file_exists:
            with open(path) as stream:
                file_content = yaml.full_load(stream)

                if file_content is not None:
                    self.read_items(file_content.items())

    def read_items(self, items, order = 0, prefix = None):
        for k, v in items:
            if prefix is None:
                key = k
            else:
                key = "{prefix}.{k}".format(prefix=prefix, k=k)

            if type(v) is str:
                self.entities[key] = (YAMLKVEntity(order, key, v, v))
                order += 1

            if type(v) is dict:
                order = self.read_items(v.items(), order, key)

        return order

    def save(self, locale):
        root = dict()

        with open(self.path, 'w', buffering=20 * (1024 ** 2)) as stream:
            # Set the non nested keys first
            for key, value in self.entities.items():
                if None in value.strings and value.key.find(".") == -1:
                    nested_set(root, value.key.split("."), value.strings[None])

            yaml.safe_dump(root, stream)
            root = dict()

            # Set the nested keys second
            for key, value in self.entities.items():
                if None in value.strings and value.key.find(".") != -1:
                    nested_set(root, value.key.split("."), value.strings[None])

            if len(root) > 0:
                yaml.safe_dump(root, stream)

    @property
    def translations(self):
        return sorted(self.entities.values(), key=lambda e: e.order)

def parse(path, source_path=None, locale=None):
    print(source_path)

    if source_path is not None:
        source_resource = YAMLResource(source_path)
    else:
        source_resource = None

    return YAMLResource(path, source_resource)
