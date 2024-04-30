"""
Parser for key-value JSON, a nested Object structure of String values.
This implementation does not supports plurals.

Each key can be associated with either a String or an Object value.
Therefore, the format support nested values.

A key can contain any character.
Nested keys are internally stored as a JSON array.
"""
import json
import logging

from pontoon.sync.exceptions import SyncError
from pontoon.sync.vcs.translation import VCSTranslation
from pontoon.sync.formats.base_json_file import JSONResource, parse as parseJSONResource

log = logging.getLogger(__name__)

SCHEMA = {
    "type": "object",
    "patternProperties": {
        ".+": {"anyOf": [{"type": "string"}, {"type": "object", "$ref": "#"}]}
    },
    "additionalProperties": False,
}


class JSONKVEntity(VCSTranslation):
    """
    Represents an entity in a Key Value JSON file.
    """

    def __init__(self, order, key, context, source_value, value):
        super().__init__(
            order=order,
            key=key,
            context=context,
            source_string=source_value,
            strings={None: value}
            if value
            else {},  # No plural support in key value JSON
            comments=[],
            fuzzy=False,
        )


class JSONKVResource(JSONResource):
    def __init__(self, path, source_resource=None):
        self.path = path
        self.entities = {}
        self.source_resource = source_resource

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = JSONKVEntity(
                    entity.order, entity.key, entity.context, "", None
                )

        self.json_file = self.open_json_file(
            path, SCHEMA, source_resource=source_resource
        )

        self.order_count = 0

        # Callback used to populate JSON Entities
        def readEntity(internal_key, dot_key, value):
            self.entities[internal_key] = JSONKVEntity(
                self.order_count, internal_key, dot_key, value, value
            )
            self.order_count += 1

        # Read all nested values
        self.traverse_json(self.json_file, readEntity)

    def save(self, locale):
        """
        Load the source resource, modify it with changes made to this
        Resource instance, and save it over the locale-specific
        resource.
        """
        if not self.source_resource:
            raise SyncError(
                "Cannot save JSON resource {}: No source resource given.".format(
                    self.path
                )
            )

        json_file = self.open_json_file(self.source_resource.path, SCHEMA)

        def writeEntity(internal_key, dot_key, value):
            entity = self.entities[internal_key]
            if entity.strings:
                self.set_json_value(json_file, internal_key, entity.strings[None])
            else:
                self.del_json_value(json_file, internal_key)

        self.traverse_json(json_file.copy(), writeEntity)
        self.clear_empty_objects(json_file)

        self.save_json_file(json_file)

    # Recursively read json object
    # Callback a function when reaching the end of a branch
    def traverse_json(self, data, function, keys=[]):
        for key, value in data.copy().items():
            currentKey = keys.copy()
            currentKey.append(key)
            if isinstance(value, dict):
                self.traverse_json(value, function, keys=currentKey)
            elif type(value) == str:
                internal_key = json.dumps(currentKey)
                dot_key = ".".join(currentKey)
                function(internal_key, dot_key, value)

    # Set json entry at dot_key path
    def set_json_value(self, json_object, internal_key, value):
        json_pointer = json_object
        for key_fragment in json.loads(internal_key)[:-1]:
            json_pointer = json_pointer[key_fragment]
        json_pointer[json.loads(internal_key)[-1]] = value

    # Remove json entry at dot_key path
    def del_json_value(self, json_object, internal_key):
        json_pointer = json_object
        split_key = json.loads(internal_key)
        for key_fragment in split_key[:-1]:
            json_pointer = json_pointer[key_fragment]
        del json_pointer[json.loads(internal_key)[-1]]

    # Recursively clear empty dict in json file
    def clear_empty_objects(self, json_object):
        for key, value in json_object.copy().items():
            if isinstance(value, dict):
                self.clear_empty_objects(json_object[key])
                if len(json_object[key]) == 0:
                    del json_object[key]


def parse(path, source_path=None, locale=None):
    return parseJSONResource(
        path, JSONKVResource, source_path=source_path, locale=locale
    )
