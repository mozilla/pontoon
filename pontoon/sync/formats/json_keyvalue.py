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


def parse(path: str):
    try:
        with open(path, "r", encoding="utf-8") as resource:
            json_file = load(resource)
            validate(json_file, SCHEMA)
    except (OSError, ValueError, ValidationError) as err:
        raise ParseError(err)

    translations: list[VCSTranslation] = []
    order = 0

    def traverse_json(data: dict[str, Any], keys: list[str]):
        nonlocal order
        for key, value in data.items():
            currentKey = [*keys, key]
            if isinstance(value, dict):
                traverse_json(value, keys=currentKey)
            elif isinstance(value, str):
                key_ = dumps(currentKey)
                translations.append(
                    VCSTranslation(
                        key=key_,
                        context=".".join(currentKey),
                        order=order,
                        strings={None: value} if value else {},
                        source_string=value,
                    )
                )
                order += 1

    # Read all nested values
    traverse_json(json_file, [])

    return translations
