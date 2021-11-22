"""
Parser for key-value JSON, a nested Object structure of String values.
This implementation does not support plurals.

You are free to use dots in the keys name on Pontoon,
though if your implementation supports nested values, you may encounter issues.
Dot is usually the separator used to represent a path to nested values.
Depending on the implementation, accessing "my.key" could either refer to
{
    "my": {
        "key": "value"
    }
}
or
{
    "my.key": "value"
}
"""
import codecs
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
    "patternProperties": {
        ".+": {"anyOf": [{"type": "string"}, {"type": "object", "$ref": "#"}]}
    },
    "additionalProperties": False,
}


class JSONEntity(VCSTranslation):
    """
    Represents an entity in a Key Value JSON file.
    """

    def __init__(self, order, key, context, source_value, value):
        super().__init__(
            key=key,
            context=context,
            source_string=source_value,
            strings={None: value}
            if value
            else {},  # No plural support in key value JSON
            comments=[],
            fuzzy=False,
        )


class JSONResource(ParsedResource):
    def __init__(self, path, source_resource=None):
        self.path = path
        self.entities = {}
        self.source_resource = source_resource

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = JSONEntity(
                    entity.order, entity.key, entity.context, "", None
                )

        try:
            with codecs.open(path, "r", "utf-8") as resource:
                self.json_file = json.load(resource)
                validate(self.json_file, SCHEMA)

        except (OSError, ValueError, ValidationError) as err:
            # If the file doesn't exist or cannot be decoded,
            # but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        self.order_count = 0

        # Callback Populate JSON Entities
        def readEntity(internal_key, dot_key, value):
            self.entities[internal_key] = JSONEntity(
                self.order_count, internal_key, dot_key, value, value
            )
            self.order_count += 1

        self.traverse_json(self.json_file, readEntity)

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
                "Cannot save JSON resource {}: No source resource given.".format(
                    self.path
                )
            )

        with codecs.open(self.source_resource.path, "r", "utf-8") as resource:
            json_file = json.load(resource, object_pairs_hook=OrderedDict)

        def writeEntity(internal_key, dot_key, value):
            entity = self.entities[internal_key]
            if entity.strings:
                self.set_json_value(json_file, internal_key, entity.strings[None])
            else:
                self.del_json_value(json_file, internal_key)

        self.traverse_json(json_file.copy(), writeEntity)
        self.clear_empty_objects(json_file)

        create_parent_directory(self.path)

        with codecs.open(self.path, "w+", "utf-8") as f:
            log.debug("Saving file: %s", self.path)
            f.write(
                json.dumps(
                    json_file, ensure_ascii=False, indent=2, separators=(",", ": ")
                )
            )
            f.write("\n")  # Add newline

    # Recursively read json object
    # Callback a function when reaching the end of a branch
    def traverse_json(self, data, function, keys=[]):
        for key, value in data.copy().items():
            currentKey = keys.copy()
            currentKey.append(key)
            if isinstance(value, dict):
                self.traverse_json(value, function, keys=currentKey)
            elif type(value) == str:
                internal_key = "<dot>".join(currentKey)
                dot_key = ".".join(currentKey)
                function(internal_key, dot_key, value)

    # Set json entry at dot_key path
    def set_json_value(self, json, internal_key, value):
        json_pointer = json
        for key_fragment in internal_key.split("<dot>")[:-1]:
            json_pointer = json_pointer[key_fragment]
        json_pointer[internal_key.split("<dot>")[-1]] = value

    # Remove json entry at dot_key path
    def del_json_value(self, json, internal_key):
        json_pointer = json
        split_key = internal_key.split("<dot>")
        for key_fragment in split_key[:-1]:
            json_pointer = json_pointer[key_fragment]
        del json_pointer[internal_key.split("<dot>")[-1]]

    # Recursively clear empty dict in json file
    def clear_empty_objects(self, json):
        for key, value in json.copy().items():
            if isinstance(value, dict):
                self.clear_empty_objects(json[key])
                if len(json[key]) == 0:
                    del json[key]


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = JSONResource(source_path)
    else:
        source_resource = None

    return JSONResource(path, source_resource)
