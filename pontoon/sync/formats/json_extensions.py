"""
Parser for the .json translation format as used by the WebExtensions API:
https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization

See also:
https://www.chromium.org/developers/design-documents/extensions/how-the-extension-system-works/i18n
"""
import codecs
import copy
import json
import logging

from collections import OrderedDict
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from pontoon.sync.exceptions import ParseError, SyncError
from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.utils import create_parent_directory
from pontoon.sync.vcs.models import VCSTranslation


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


class JSONEntity(VCSTranslation):
    """
    Represents an entity in a JSON file.
    """

    def __init__(self, order, key, data):
        self.key = key
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


class JSONResource(ParsedResource):
    def __init__(self, path, source_resource=None):
        self.path = path
        self.entities = {}
        self.source_resource = source_resource

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                data = copy.copy(entity.data)
                data["message"] = None

                self.entities[key] = JSONEntity(entity.order, entity.key, data,)

        try:
            with codecs.open(path, "r", "utf-8") as resource:
                self.json_file = json.load(resource, object_pairs_hook=OrderedDict)
                validate(self.json_file, SCHEMA)

        except (IOError, ValueError, ValidationError) as err:
            # If the file doesn't exist or cannot be decoded,
            # but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        for order, (key, data) in enumerate(self.json_file.items()):
            self.entities[key] = JSONEntity(order, key, data,)

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
            raise SyncError(
                "Cannot save JSON resource {0}: No source resource given.".format(
                    self.path
                )
            )

        with codecs.open(self.source_resource.path, "r", "utf-8") as resource:
            json_file = json.load(resource, object_pairs_hook=OrderedDict)

            try:
                validate(json_file, SCHEMA)
            except ValidationError as e:
                raise ParseError(e)

        # Iterate over a copy, leaving original free to modify
        for key, value in json_file.copy().items():
            entity = self.entities[key]

            if entity.strings:
                json_file[key]["message"] = entity.strings[None]
            else:
                del json_file[key]

        create_parent_directory(self.path)

        with codecs.open(self.path, "w+", "utf-8") as f:
            log.debug("Saving file: %s", self.path)
            f.write(
                json.dumps(
                    json_file, ensure_ascii=False, indent=2, separators=(",", ": ")
                )
            )
            f.write("\n")  # Add newline


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = JSONResource(source_path)
    else:
        source_resource = None

    return JSONResource(path, source_resource)
