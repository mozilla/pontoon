from __future__ import annotations

import codecs

from fluent.syntax import FluentParser, FluentSerializer, ast

from .common import ParseError, VCSTranslation


parser = FluentParser()
serializer = FluentSerializer()


class FTLResource:
    entities: dict[str, VCSTranslation]

    def __init__(self, path, source_resource: "FTLResource" | None = None):
        # Use entities from the source_resource if it's available.
        if source_resource:
            self.entities = source_resource.entities
            for entity in self.entities.values():
                entity.strings = {}
        else:
            self.entities = {}

        try:
            with codecs.open(path, "r", "utf-8") as resource:
                structure = parser.parse(resource.read())
        # Parse errors are handled gracefully by fluent
        # No need to catch them here
        except OSError as err:
            # If the file doesn't exist, but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        group_comment: list[str] = []
        resource_comment: list[str] = []
        order = 0
        for obj in structure.body:
            if isinstance(obj, (ast.Message, ast.Term)):
                key = obj.id.name
                if isinstance(obj, ast.Term):
                    key = "-" + key

                # Do not store comments in the string column
                comment = obj.comment.content if obj.comment else None
                obj.comment = None
                translation = serializer.serialize_entry(obj)

                self.entities[key] = VCSTranslation(
                    key=key,
                    context=key,
                    order=order,
                    strings={None: translation},
                    source_string=translation,
                    comments=[comment] if comment else None,
                    group_comments=group_comment,
                    resource_comments=resource_comment,
                )
                order += 1

            elif isinstance(obj, ast.GroupComment):
                group_comment = [obj.content] if obj.content else []

            elif isinstance(obj, ast.ResourceComment) and obj.content:
                resource_comment.append(obj.content)


def parse(path, source_path=None):
    source_resource = None if source_path is None else FTLResource(source_path)
    res = FTLResource(path, source_resource)
    return sorted(res.entities.values(), key=lambda e: e.order)
