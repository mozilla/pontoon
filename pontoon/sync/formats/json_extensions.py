"""
Parser for the .json translation format as used by the WebExtensions API:
https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization

See also:
https://www.chromium.org/developers/design-documents/extensions/how-the-extension-system-works/i18n
"""

from __future__ import annotations

from json import load

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from .common import ParseError, VCSTranslation


SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "description": {"type": "string"},
            "placeholders": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "example": {"type": "string"},
                    },
                    "required": ["content"],
                },
            },
        },
        "required": ["message"],
    },
}


def parse(path: str):
    try:
        with open(path, "r", encoding="utf-8") as resource:
            json_file = load(resource)
            validate(json_file, SCHEMA)
    except (OSError, ValueError, ValidationError) as err:
        raise ParseError(err)

    return [
        VCSTranslation(
            key=key,
            context=key,
            order=order,
            strings={None: string} if (string := data["message"]) else {},
            source_string=string,
            comments=[data["description"]] if "description" in data else None,
            source=data.get("placeholders", []),
        )
        for order, (key, data) in enumerate(json_file.items())
    ]
