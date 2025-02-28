import codecs
import json
import logging

from collections import OrderedDict

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.formats.exceptions import ParseError


log = logging.getLogger(__name__)


class JSONResource(ParsedResource):
    @property
    def translations(self):
        return sorted(self.entities.values(), key=lambda e: e.order)

    def open_json_file(self, path, SCHEMA, source_resource=None):
        try:
            with codecs.open(path, "r", "utf-8") as resource:
                json_file = json.load(resource, object_pairs_hook=OrderedDict)
                validate(json_file, SCHEMA)
                return json_file

        except (OSError, ValueError, ValidationError) as err:
            # If the file doesn't exist or cannot be decoded,
            # but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return {}
            else:
                raise ParseError(err)


def parse(path, JSONResource, source_path=None, locale=None):
    if source_path is not None:
        source_resource = JSONResource(source_path)
    else:
        source_resource = None

    return JSONResource(path, source_resource)
