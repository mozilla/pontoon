
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import cached_property

from pontoon.base.utils import glob_to_regex
from pontoon.tags.models import Tag

from .base import Clonable
from .resources import TagsResourcesTool
from .stats import TagsStatsTool
from .tag import TagEncoder, TagTool
from .translations import TagsLatestTranslationsTool


class ProjectTagsEncoder(DjangoJSONEncoder):

    def default(self, obj):
        if isinstance(obj, TagsTool):
            return dict(data=[tag for tag in obj])
        elif isinstance(obj, TagTool):
            return TagEncoder().default(obj)
        return super(ProjectTagsEncoder, self).default(obj)


class TagsTool(Clonable):
    """This provides an API for retrieving related ``Tags`` for given filters,
    providing breakdowns of statistical information about the ``Tags``, and
    managing ``Tags`` used in the site.
    """

    tag_class = TagTool
    resources_class = TagsResourcesTool
    translations_class = TagsLatestTranslationsTool
    stats_class = TagsStatsTool
    clone_kwargs = [
        'locales',
        'projects',
        'priority',
        'path',
        'slug']

    def __getitem__(self, k):
        return self(slug=k)

    def __iter__(self):
        return self.iter_tags(self.stat_tool.data)

    def __len__(self):
        return len(self.stat_tool.data)

    def get_tags(self, slug=None):
        tags = self.tag_manager.values(
            "pk", "name", "slug", "priority", "project")
        if slug:
            return tags.filter(slug__regex=glob_to_regex(slug))
        return tags

    @property
    def tag_manager(self):
        return Tag.objects

    @cached_property
    def resource_tool(self):
        return self.resources_class(
            projects=self.projects,
            locales=self.locales,
            slug=self.slug,
            path=self.path)

    @cached_property
    def stat_tool(self):
        return self.stats_class(
            slug=self.slug,
            locales=self.locales,
            projects=self.projects,
            priority=self.priority,
            path=self.path)

    @cached_property
    def translation_tool(self):
        return self.translations_class(
            slug=self.slug,
            locales=self.locales,
            projects=self.projects)

    def create(self, slug, name=None, project=None):
        created = self.tag_manager.create(
            slug=slug,
            project=project,
            name=name or slug.capitalize().replace('-', ' '))
        return self.tag_class(
            self,
            pk=created.pk,
            name=created.name,
            slug=created.slug,
            priority=created.priority,
            project=created.project)

    def delete(self, slug):
        return self.tag_manager.get(slug=slug).delete()

    def get(self, slug=None):
        if slug is None:
            return list(self)[0]
        return self.tag_class(self, **self.get_tags(slug=slug)[0])

    def iter_tags(self, tags):
        for tag in tags:
            latest_translation = self.translation_tool.data.get(
                tag["resource__tag"])
            yield self.tag_class(
                self,
                latest_translation=latest_translation,
                **tag)
