import codecs
import copy
import logging

from fluent.syntax import FluentParser, FluentSerializer, ast

from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.formats.exceptions import ParseError
from pontoon.sync.vcs.translation import VCSTranslation


log = logging.getLogger(__name__)


parser = FluentParser()
serializer = FluentSerializer()
localizable_entries = (ast.Message, ast.Term)


class FTLEntity(VCSTranslation):
    """
    Represents entities in FTL (without its attributes).
    """

    def __init__(
        self,
        key,
        source_string,
        source_string_plural,
        strings,
        comments=None,
        group_comments=None,
        resource_comments=None,
        order=None,
    ):
        super().__init__(
            key=key,
            context=key,
            source_string=source_string,
            source_string_plural=source_string_plural,
            strings=strings,
            comments=comments or [],
            group_comments=group_comments or [],
            resource_comments=resource_comments or [],
            fuzzy=False,
            order=order,
        )

    def __repr__(self):
        return "<FTLEntity {key}>".format(key=self.key.encode("utf-8"))


class FTLResource(ParsedResource):
    def __init__(self, path, locale, source_resource=None):
        self.path = path
        self.locale = locale
        self.entities = {}
        self.order = 0

        # Copy entities from the source_resource if it's available.
        if source_resource:
            for key, entity in source_resource.entities.items():
                self.entities[key] = FTLEntity(
                    entity.key,
                    "",
                    "",
                    {},
                    copy.copy(entity.comments),
                    copy.copy(entity.group_comments),
                    copy.copy(entity.resource_comments),
                    entity.order,
                )

        try:
            with codecs.open(path, "r", "utf-8") as resource:
                self.structure = parser.parse(resource.read())
        # Parse errors are handled gracefully by fluent
        # No need to catch them here
        except OSError as err:
            # If the file doesn't exist, but we have a source resource,
            # we can keep going, we'll just not have any translations.
            if source_resource:
                return
            else:
                raise ParseError(err)

        group_comment = []
        resource_comment = []
        for obj in self.structure.body:
            if isinstance(obj, localizable_entries):
                key = get_key(obj)
                comment = [obj.comment.content] if obj.comment else []

                # Do not store comments in the string column
                obj.comment = None
                translation = serializer.serialize_entry(obj)

                self.entities[key] = FTLEntity(
                    key,
                    translation,
                    "",
                    {None: translation},
                    comment,
                    group_comment,
                    resource_comment,
                    self.order,
                )
                self.order += 1

            elif isinstance(obj, ast.GroupComment):
                group_comment = [obj.content]

            elif isinstance(obj, ast.ResourceComment):
                resource_comment += [obj.content]

    @property
    def translations(self):
        return sorted(self.entities.values(), key=lambda e: e.order)


def get_key(obj):
    """
    Get FTL Message/Term key as it appears in the file.
    In case of a Term, we need to prepend -. See bug 1521523.
    """
    key = obj.id.name

    if isinstance(obj, ast.Term):
        return "-" + key

    return key


def parse(path, source_path=None, locale=None):
    if source_path is not None:
        source_resource = FTLResource(source_path, locale)
    else:
        source_resource = None
    return FTLResource(path, locale, source_resource)
