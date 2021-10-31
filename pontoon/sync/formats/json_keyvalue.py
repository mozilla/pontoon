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

class JSONEntity(VCSTranslation):
    """
    Represents an entity in a Key Value JSON file.
    """

    def __init__(self, order, key, source_value, value):
        super().__init__(
            key=key,
            context=key,
            source_string=source_value,
            strings={None: value}, # No plural support in key value JSON
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
                self.entities[key] = JSONEntity(entity.order, entity.key, "", None)

        try:
            with codecs.open(path, "r", "utf-8") as resource:
                self.json_file = json.load(resource)

        except (OSError, ValueError, ValidationError) as err:
            # If the file doesn't exist or cannot be decoded,
            # but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        self.order_count = 0
        def readEntity(flat_key, value):
            self.entities[flat_key] = JSONEntity(self.order_count, flat_key, value, value)
            self.order_count += 1
        self.traverse_json(self.json_file, readEntity)

    def traverse_json(self, data, function, keys = []):
        for key, value in data.items():
            currentKey = keys.copy()
            currentKey.append(key)
            if type(value) == dict:
                self.traverse_json(value, function, keys = currentKey)
            elif type(value) == str:
                flat_key = ".".join(currentKey)
                function(flat_key, value)

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

        def writeEntity(flat_key, value):
            entity = self.entities[flat_key]
            if entity.strings:
                print(entity)
                self.get_value_flat_key(json_file, flat_key)
                self.set_value_flat_key(json_file, flat_key, entity.strings[None])
                self.get_value_flat_key(json_file, flat_key)
                print()
            else:
                del value

        self.traverse_json(json_file.copy(), writeEntity)

        create_parent_directory(self.path)

        with codecs.open(self.path, "w+", "utf-8") as f:
            log.debug("Saving file: %s", self.path)
            f.write(
                json.dumps(
                    json_file, ensure_ascii=False, indent=2, separators=(",", ": ")
                )
            )
            f.write("\n")  # Add newline

    def get_value_flat_key(self, json, flat_key):
        json_pointer = json
        for key_fragment in flat_key.split("."):
            json_pointer = json_pointer[key_fragment]
        return json_pointer

    def set_value_flat_key(self, json, flat_key, value):
        json_pointer = json
        for key_fragment in flat_key.split("."):
            json_pointer = json_pointer[key_fragment]
        json_pointer = value


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = JSONResource(source_path)
    else:
        source_resource = None

    return JSONResource(path, source_resource)
