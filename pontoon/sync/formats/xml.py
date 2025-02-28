"""
Parser for the strings.xml file format.
"""

from __future__ import annotations

from compare_locales import parser

from .common import ParseError, VCSTranslation


class XMLResource:
    entities: dict[str, VCSTranslation]

    def __init__(self, path, source_resource: "XMLResource" | None = None):
        # Use entities from the source_resource if it's available.
        if source_resource:
            self.entities = source_resource.entities
            for entity in self.entities.values():
                entity.strings = {}
        else:
            self.entities = {}

        try:
            xml_parser = parser.getParser(path)
            xml_parser.readFile(path)
        except UserWarning as err:
            raise ParseError(err)
        except OSError as err:
            # If the file doesn't exist, but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        order = 0
        for entity in xml_parser.walk():
            if isinstance(entity, parser.Entity):
                key = entity.key
                string = entity.unwrap().replace("\\'", "'")
                comments = (
                    entity.pre_comment.val.split("\n") if entity.pre_comment else []
                )
                self.entities[key] = VCSTranslation(
                    key=key,
                    context=key,
                    order=order,
                    strings={None: string} if string is not None else {},
                    source_string=string,
                    comments=comments,
                )
                order += 1


def parse(path, source_path=None):
    source_resource = None if source_path is None else XMLResource(source_path)
    res = XMLResource(path, source_resource)
    return sorted(res.entities.values(), key=lambda e: e.order)
