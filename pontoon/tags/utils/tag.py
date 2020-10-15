from django.utils.functional import cached_property

from .tagged import Tagged, TaggedLocale


class TagTool(Tagged):
    """This wraps ``Tag`` model kwargs providing an API for
    efficient retrieval of related information, eg tagged ``Resources``,
    ``Locales`` and ``Projects``, and methods for managing linked
    ``Resources``.
    """

    def __init__(self, tags_tool, **kwargs):
        self.tags_tool = tags_tool
        self.name = kwargs.pop("name")
        self.pk = kwargs.pop("pk")
        self.priority = kwargs.pop("priority")
        self.slug = kwargs.pop("slug")
        self.project = kwargs.pop("project")
        super(TagTool, self).__init__(**kwargs)

    @property
    def linkable_resources(self):
        """``Resources`` that could be linked to this ``Tag``"""
        return self.resource_tool.get_linkable_resources(self.slug).order_by("path")

    @property
    def linked_resources(self):
        """``Resources`` that are linked to this ``Tag``"""
        return self.resource_tool.get_linked_resources(self.slug).order_by("path")

    @property
    def locale_stats(self):
        return self.tags_tool.stat_tool(slug=self.slug, groupby="locale").data

    @cached_property
    def locale_latest(self):
        """A cached property containing latest locale changes
        """
        return self.tags_tool.translation_tool(slug=self.slug, groupby="locale").data

    @cached_property
    def object(self):
        """Returns the ``Tag`` model object for this tag.
        This is useful for introspection, but should be avoided in
        actual code
        """
        return self.tags_tool.tag_manager.select_related("project").get(pk=self.pk)

    @cached_property
    def resource_tool(self):
        """This is a cached version of a TagsResourcesTool, and is used
        for retrieving un/linked information about resources.

        If the the tag's project is not set, then it uses the resource_tool
        provided by tags_tool, otherwise it clones tags_tool, setting projects
        to [self.project] to ensure we only retrieve the correct information.
        """
        return (
            self.tags_tool.resource_tool(projects=[self.project])
            if self.project
            else self.tags_tool.resource_tool
        )

    def iter_locales(self, project=None):
        """Iterate ``Locales`` that are associated with this tag
        (given any filtering in ``self.tags_tool``)

        yields a ``TaggedLocale`` that can be used to get eg chart data
        """
        for locale in self.locale_stats:
            yield TaggedLocale(
                project=project,
                latest_translation=self.locale_latest.get(locale["locale"]),
                **locale
            )

    def link_resources(self, resources):
        """Link Resources to this tag, raises an Error if the tag's
        Project is set, and the requested resource is not in  that Project
        """
        return self.resource_tool.link(self.slug, resources=resources)

    def unlink_resources(self, resources):
        """Unlink Resources from this tag
        """
        return self.resource_tool.unlink(self.slug, resources=resources)
