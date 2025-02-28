"""
Parser for key-value JSON, a nested Object structure of String values.
This implementation does not supports plurals.

Each key can be associated with either a String or an Object value.
Therefore, the format support nested values.

A key can contain any character.
Nested keys are internally stored as a JSON array.
"""

from __future__ import annotations

from json import dumps, load
from typing import Any

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from .common import ParseError, VCSTranslation


SCHEMA = {
    "type": "object",
    "patternProperties": {
        ".+": {"anyOf": [{"type": "string"}, {"type": "object", "$ref": "#"}]}
    },
    "additionalProperties": False,
}


class JSONKVResource:
    entities: dict[str, VCSTranslation]

    def __init__(self, path, source_resource: "JSONKVResource" | None = None):
        # Use entities from the source_resource if it's available.
        if source_resource:
            self.entities = source_resource.entities
            for entity in self.entities.values():
                entity.strings = {}
        else:
            self.entities = {}

        try:
            with open(path, "r", encoding="utf-8") as resource:
                json_file = load(resource)
                validate(json_file, SCHEMA)
        except (OSError, ValueError, ValidationError) as err:
            # If the file doesn't exist or cannot be decoded,
            # but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        order = 0

        def traverse_json(data: dict[str, Any], keys: list[str]):
            nonlocal order
            for key, value in data.items():
                currentKey = [*keys, key]
                if isinstance(value, dict):
                    traverse_json(value, keys=currentKey)
                elif isinstance(value, str):
                    key_ = dumps(currentKey)
                    self.entities[key_] = VCSTranslation(
                        key=key_,
                        context=".".join(currentKey),
                        order=order,
                        strings={None: value} if value else {},
                        source_string=value,
                    )
                    order += 1

        # Read all nested values
        traverse_json(json_file, [])


def parse(path, source_path=None):
    source_resource = None if source_path is None else JSONKVResource(source_path)
    res = JSONKVResource(path, source_resource)
    return sorted(res.entities.values(), key=lambda e: e.order)
