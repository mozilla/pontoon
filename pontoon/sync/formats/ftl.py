from __future__ import annotations

from fluent.syntax import FluentParser, FluentSerializer, ast

from .common import ParseError, VCSTranslation


parser = FluentParser()
serializer = FluentSerializer()


def parse(path: str):
    try:
        with open(path, "r", encoding="utf-8") as resource:
            structure = parser.parse(resource.read())
    # Parse errors are handled gracefully by fluent
    # No need to catch them here
    except OSError as err:
        raise ParseError(err)

    translations: list[VCSTranslation] = []
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

            translations.append(
                VCSTranslation(
                    key=key,
                    context=key,
                    order=order,
                    strings={None: translation},
                    source_string=translation,
                    comments=[comment] if comment else None,
                    group_comments=group_comment,
                    resource_comments=resource_comment,
                )
            )
            order += 1

        elif isinstance(obj, ast.GroupComment):
            group_comment = [obj.content] if obj.content else []

        elif isinstance(obj, ast.ResourceComment) and obj.content:
            resource_comment.append(obj.content)

    return translations
