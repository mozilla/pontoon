"""
Parser for silme-compatible translation formats.
"""

import codecs

from collections import OrderedDict
from copy import copy

import silme

from silme.format.dtd import FormatParser as DTDParser
from silme.format.inc import FormatParser as IncParser
from silme.format.ini import FormatParser as IniParser
from silme.format.properties import FormatParser as PropertiesParser

from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.formats.exceptions import ParseError
from pontoon.sync.vcs.translation import VCSTranslation


class SilmeEntity(VCSTranslation):
    def __init__(self, silme_object, comments=None, order=0, copy_string=True):
        """
        :param copy_string:
            If True, copy the string from the silme_object. Otherwise,
            self.strings will be an empty dict. Used for creating empty
            copies of translations from source resources.
        """
        self.silme_object = silme_object
        self.comments = comments or []
        self.order = order

        if copy_string:
            self.strings = {None: self.silme_object.value}
        else:
            self.strings = {}

    @property
    def key(self):
        return self.silme_object.id

    @property
    def context(self):
        return self.key

    @property
    def source_string(self):
        return self.silme_object.value

    @property
    def source_string_plural(self):
        return ""

    @property
    def fuzzy(self):
        return False

    @fuzzy.setter
    def fuzzy(self, fuzzy):
        pass  # We don't use fuzzy in silme

    @property
    def source(self):
        return []

    def __eq__(self, other):
        return self.key == other.key and self.strings.get(None) == other.strings.get(
            None
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        # python 3
        return bool(self.strings)


class SilmeResource(ParsedResource):
    def __init__(self, parser, path, source_resource=None):
        self.parser = parser
        self.path = path
        self.entities = OrderedDict()  # Preserve entity order.

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = copy_source_entity(entity)

        try:
            # Only uncomment MOZ_LANGPACK_CONTRIBUTORS if this is a .inc
            # file and a source resource (i.e. it has no source resource
            # itself).
            self.structure = parser.get_structure(
                read_file(
                    path,
                    uncomment_moz_langpack=parser is IncParser and not source_resource,
                )
            )
        # Parse errors are handled gracefully by silme
        # No need to catch them here
        except OSError as err:
            # If the file doesn't exist, but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        comments = []
        current_order = 0
        for obj in self.structure:
            if isinstance(obj, silme.core.entity.Entity):
                entity = SilmeEntity(obj, comments, current_order)
                self.entities[entity.key] = entity
                current_order += 1
                comments = []
            elif isinstance(obj, silme.core.structure.Comment):
                for comment in obj:
                    # Silme groups comments together, so we strip
                    # whitespace and split them up.
                    lines = str(comment).strip().split("\n")
                    comments += [line.strip() for line in lines]

    @property
    def translations(self):
        return list(self.entities.values())


def read_file(path, uncomment_moz_langpack=False):
    """Read the resource at the given path."""
    with codecs.open(path, "r", "utf-8") as f:
        # .inc files have a special commented-out entity called
        # MOZ_LANGPACK_CONTRIBUTORS. We optionally un-comment it before
        # parsing so locales can translate it.
        if uncomment_moz_langpack:
            lines = []
            for line in f:
                if line.startswith("# #define MOZ_LANGPACK_CONTRIBUTORS"):
                    line = line[2:]
                lines.append(line)
            content = "".join(lines)
        else:
            content = f.read()

    return content


def copy_source_entity(entity):
    """
    Copy an entity from a source file to a new SilmeEntity instance.
    The new copy will have an empty strings attribute so that entities
    that are copied but not modified during sync will not be saved in
    the translated resource.
    """
    return SilmeEntity(
        entity.silme_object,
        copy(entity.comments),  # Members are strings, shallow is fine.
        entity.order,
        copy_string=False,
    )


def parse(parser, path, source_path=None, locale=None):
    # TODO: Cache the source resource to avoid re-parsing it a bunch.
    if source_path is not None:
        source_resource = SilmeResource(parser, source_path)
    else:
        source_resource = None

    return SilmeResource(parser, path, source_resource=source_resource)


def parse_properties(path, source_path=None, locale=None):
    return parse(PropertiesParser, path, source_path)


def parse_ini(path, source_path=None, locale=None):
    return parse(IniParser, path, source_path)


def parse_inc(path, source_path=None, locale=None):
    return parse(IncParser, path, source_path)


def parse_dtd(path, source_path=None, locale=None):
    return parse(DTDParser, path, source_path)
