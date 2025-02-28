"""
Parser for silme-compatible translation formats.
"""

from __future__ import annotations

from typing import Type

from silme.core.entity import Entity as SilmeEntity
from silme.core.structure import Comment as SilmeComment
from silme.format.dtd import FormatParser as DTDParser
from silme.format.inc import FormatParser as IncParser
from silme.format.ini import FormatParser as IniParser
from silme.format.properties import FormatParser as PropertiesParser

from .common import ParseError, VCSTranslation


class SilmeResource:
    entities: dict[str, VCSTranslation]

    def __init__(
        self,
        parser: Type[DTDParser | IncParser | IniParser | PropertiesParser],
        path,
        source_resource: "SilmeResource" | None = None,
    ):
        # Use entities from the source_resource if it's available.
        if source_resource:
            self.entities = source_resource.entities
            for entity in self.entities.values():
                entity.strings = {}
        else:
            self.entities = {}

        try:
            # Only uncomment MOZ_LANGPACK_CONTRIBUTORS if this is a .inc
            # file and a source resource (i.e. it has no source resource
            # itself).
            structure = parser.get_structure(
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

        comments: list[str] = []
        order = 0
        for obj in structure:
            if isinstance(obj, SilmeEntity):
                key = obj.id
                string = obj.value
                self.entities[key] = VCSTranslation(
                    key=key,
                    context=key,
                    order=order,
                    strings={None: string},
                    source_string=string,
                    comments=comments,
                )
                comments = []
                order += 1
            elif isinstance(obj, SilmeComment):
                for comment in obj:
                    # Silme groups comments together, so we strip
                    # whitespace and split them up.
                    lines = str(comment).strip().split("\n")
                    comments += [line.strip() for line in lines]


def read_file(path, uncomment_moz_langpack=False):
    """Read the resource at the given path."""
    with open(path, "r", encoding="utf-8") as f:
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


def parse(parser, path, source_path=None):
    source_resource = (
        None if source_path is None else SilmeResource(parser, source_path)
    )
    res = SilmeResource(parser, path, source_resource=source_resource)
    return list(res.entities.values())


def parse_properties(path, source_path=None):
    return parse(PropertiesParser, path, source_path)


def parse_ini(path, source_path=None):
    return parse(IniParser, path, source_path)


def parse_inc(path, source_path=None):
    return parse(IncParser, path, source_path)


def parse_dtd(path, source_path=None):
    return parse(DTDParser, path, source_path)
