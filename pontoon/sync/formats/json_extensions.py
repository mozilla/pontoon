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
import os

from pontoon.sync import SyncError
from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.vcs.models import VCSTranslation


log = logging.getLogger(__name__)


class JSONEntity(VCSTranslation):
    """
    Represents an entity in a JSON file.
    """
    def __init__(self, order, key, data):
        self.key = key
        self.data = data
        self.order = order
        self.strings = {None: self.source_string} if self.source_string else {}
        self.last_translator = None
        self.last_update = None

    @property
    def source_string(self):
        return self.data['message']

    @property
    def source_string_plural(self):
        return ''

    @property
    def comments(self):
        return [self.data['description']] if 'description' in self.data else []

    @property
    def fuzzy(self):
        return False

    @fuzzy.setter
    def fuzzy(self, fuzzy):
        pass  # We don't use fuzzy in JSON

    @property
    def source(self):
        return self.data['placeholders'] if 'placeholders' in self.data else []


class JSONResource(ParsedResource):
    def __init__(self, path, source_resource=None):
        self.path = path
        self.entities = {}
        self.source_resource = source_resource

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = JSONEntity(
                    entity.order,
                    entity.key,
                    copy.copy(entity.data),
                )

        try:
            with codecs.open(path, 'r', 'utf-8') as resource:
                content = resource.read()
                self.json_file = json.loads(content)
        except IOError:
            # If the file doesn't exist, but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise

        for order, unit in enumerate(self.json_file.items()):
            key = unit[0]
            data = unit[1]
            self.entities[key] = JSONEntity(
                order,
                key,
                data,
            )

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
            raise SyncError('Cannot save FTL resource {0}: No source resource given.'
                            .format(self.path))

        with codecs.open(self.source_resource.path, 'r', 'utf-8') as resource:
            json_file = json.loads(resource.read())

        # Iterate over a copy, leaving original free to modify
        for key, value in json_file.copy().items():
            entity = self.entities[key]

            if entity.strings:
                json_file[key]['message'] = entity.strings[None]
            else:
                del json_file[key]

        # Create parent directory if it doesn't exist.
        try:
            os.makedirs(os.path.dirname(self.path))
        except OSError:
            pass  # Already exists, phew!

        with codecs.open(self.path, 'w+', 'utf-8') as f:
            f.write(json.dumps(json_file, indent=4))
            log.debug('Saved file: %s', self.path)


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = JSONResource(source_path)
    else:
        source_resource = None

    return JSONResource(path, source_resource)
