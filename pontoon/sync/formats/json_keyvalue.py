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

from pontoon.sync.formats.base_json_file import JSONResource, parse as parseJSONResource
from pontoon.sync.vcs.translation import VCSTranslation


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

    # Recursively read json object
    # Callback a function when reaching the end of a branch
    def traverse_json(self, data, function, keys=[]):
        for key, value in data.copy().items():
            currentKey = keys.copy()
            currentKey.append(key)
            if isinstance(value, dict):
                self.traverse_json(value, function, keys=currentKey)
            elif isinstance(value, str):
                internal_key = json.dumps(currentKey)
                dot_key = ".".join(currentKey)
                function(internal_key, dot_key, value)


def parse(path, source_path=None, locale=None):
    return parseJSONResource(
        path, JSONKVResource, source_path=source_path, locale=locale
    )
