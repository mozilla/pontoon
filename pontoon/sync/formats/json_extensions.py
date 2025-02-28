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


class JSONExtensionResource:
    entities: dict[str, VCSTranslation]

    def __init__(self, path, source_resource: "JSONExtensionResource" | None = None):
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

        for order, (key, data) in enumerate(json_file.items()):
            string: str = data["message"]
            self.entities[key] = VCSTranslation(
                key=key,
                context=key,
                order=order,
                strings={None: string} if string else {},
                source_string=string,
                comments=[data["description"]] if "description" in data else None,
                source=data.get("placeholders", []),
            )


def parse(path, source_path=None):
    source_resource = (
        None if source_path is None else JSONExtensionResource(source_path)
    )
    res = JSONExtensionResource(path, source_resource)
    return sorted(res.entities.values(), key=lambda e: e.order)
