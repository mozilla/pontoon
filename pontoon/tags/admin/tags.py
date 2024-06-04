from .base import Clonable
from .resources import TagsResourcesTool
from .tag import TagTool
from django.utils.functional import cached_property
from pontoon.tags.models import Tag


class TagsTool(Clonable):
    """This provides an API for retrieving related ``Tags`` for given filters,
    providing breakdowns of statistical information about the ``Tags``, and
    managing ``Tags`` used in the site.
    """

    tag_class = TagTool
    resources_class = TagsResourcesTool
    clone_kwargs = ("locales", "projects", "priority", "path", "slug")

    def __getitem__(self, k):
        return self(slug=k)

    @property
    def tag_manager(self):
        return Tag.objects

    @cached_property
    def resource_tool(self):
        return self.resources_class(
            projects=self.projects, locales=self.locales, slug=self.slug, path=self.path
        )

    def get(self, slug=None):
        """Get the first tag by iterating self, or by slug if set"""
        if slug is None:
            return list(self)[0]
        return self.tag_class(self, **self.get_tags(slug=slug)[0])

    def get_tags(self, slug=None):
        """Get `values` of associated tags, filtering by slug if given"""
        tags = self.tag_manager.filter(project__in=self.projects).values(
            "pk", "name", "slug", "priority", "project"
        )
        if slug:
            return tags.filter(slug=slug)
        return tags
