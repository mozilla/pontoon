"""
Parser for the .json translation format as used by the WebExtensions API:
https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization

See also:
https://www.chromium.org/developers/design-documents/extensions/how-the-extension-system-works/i18n
"""

import copy
import logging

from pontoon.sync.formats.base_json_file import JSONResource, parse as parseJSONResource
from pontoon.sync.vcs.translation import VCSTranslation


log = logging.getLogger(__name__)

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


class JSONExtensionEntity(VCSTranslation):
    """
    Represents an entity in a JSON file.
    """

    def __init__(self, order, key, data):
        self.key = key
        self.context = key
        self.data = data
        self.order = order
        self.strings = {None: self.source_string} if self.source_string else {}

    @property
    def source_string(self):
        return self.data["message"]

    @property
    def source_string_plural(self):
        return ""

    @property
    def comments(self):
        return [self.data["description"]] if "description" in self.data else []

    @property
    def fuzzy(self):
        return False

    @fuzzy.setter
    def fuzzy(self, fuzzy):
        pass  # We don't use fuzzy in JSON

    @property
    def source(self):
        return self.data.get("placeholders", [])


class JSONExtensionResource(JSONResource):
    def __init__(self, path, source_resource=None):
        self.path = path
        self.entities = {}

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                data = copy.copy(entity.data)
                data["message"] = None

                self.entities[key] = JSONExtensionEntity(
                    entity.order,
                    entity.key,
                    data,
                )

        self.json_file = self.open_json_file(
            path, SCHEMA, source_resource=source_resource
        )

        for order, (key, data) in enumerate(self.json_file.items()):
            self.entities[key] = JSONExtensionEntity(
                order,
                key,
                data,
            )


def parse(path, source_path=None, locale=None):
    return parseJSONResource(
        path, JSONExtensionResource, source_path=source_path, locale=locale
    )
