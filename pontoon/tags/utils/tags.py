from django.utils.functional import cached_property

from pontoon.tags.models import Tag

from .base import Clonable
from .resources import TagsResourcesTool
from .stats import TagsStatsTool
from .tag import TagTool
from .translations import TagsLatestTranslationsTool


class TagsTool(Clonable):
    """This provides an API for retrieving related ``Tags`` for given filters,
    providing breakdowns of statistical information about the ``Tags``, and
    managing ``Tags`` used in the site.
    """

    tag_class = TagTool
    resources_class = TagsResourcesTool
    translations_class = TagsLatestTranslationsTool
    stats_class = TagsStatsTool
    clone_kwargs = ("locales", "projects", "priority", "path", "slug")

    def __getitem__(self, k):
        return self(slug=k)

    def __iter__(self):
        return self.iter_tags(self.stat_tool.data)

    def __len__(self):
        return len(self.stat_tool.data)

    @property
    def tag_manager(self):
        return Tag.objects

    @cached_property
    def resource_tool(self):
        return self.resources_class(
            projects=self.projects, locales=self.locales, slug=self.slug, path=self.path
        )

    @cached_property
    def stat_tool(self):
        return self.stats_class(
            slug=self.slug,
            locales=self.locales,
            projects=self.projects,
            priority=self.priority,
            path=self.path,
        )

    @cached_property
    def translation_tool(self):
        return self.translations_class(
            slug=self.slug, locales=self.locales, projects=self.projects
        )

    def get(self, slug=None):
        """Get the first tag by iterating self, or by slug if set
        """
        if slug is None:
            return list(self)[0]
        return self.tag_class(self, **self.get_tags(slug=slug)[0])

    def get_tags(self, slug=None):
        """Get `values` of associated tags, filtering by slug if given
        """
        tags = self.tag_manager.filter(project__in=self.projects).values(
            "pk", "name", "slug", "priority", "project"
        )
        if slug:
            return tags.filter(slug=slug)
        return tags

    def iter_tags(self, tags):
        """Iterate associated tags, and create TagTool objects for
        each, adding latest translation data
        """
        for tag in tags:
            latest_translation = self.translation_tool.data.get(tag["resource__tag"])
            yield self.tag_class(self, latest_translation=latest_translation, **tag)
