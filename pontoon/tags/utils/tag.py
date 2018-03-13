
import json

from django.urls import reverse
from django.utils.functional import cached_property

from .tagged import Tagged, TaggedLocale


class TagEncoder(json.JSONEncoder):

    def default(self, obj):
        if not isinstance(obj, TagTool):
            return obj
        project = obj.object.project
        as_dict = dict(
            slug=obj.slug,
            name=obj.name,
            url=obj.url(project=project),
            activity=obj.latest_activity and obj.latest_activity.as_dict(),
            priority=obj.object.priority,
            chart=obj.chart)
        return as_dict


class TagLocalesEncoder(TagEncoder):

    def default(self, obj):
        if not isinstance(obj, TagTool):
            return obj
        as_dict = super(TagLocalesEncoder, self).default(obj)
        project = obj.object.project
        as_dict['data'] = list(
            locale.as_dict()
            for locale
            in obj.iter_locales(project=project))
        return as_dict


class TagTool(Tagged):
    """This wraps a ``Tag`` model object providing an API for
    efficient retrieval of related information, eg tagged ``Resources``,
    ``Locales`` and ``Projects``, and methods for managing linked
    ``Resources``.
    """

    def __init__(self, tags_tool, **kwargs):
        self.tags_tool = tags_tool
        self._name = kwargs.pop("name")
        self._pk = kwargs.pop("pk")
        self._priority = kwargs.pop("priority")
        self._slug = kwargs.pop("slug")
        self._project = kwargs.pop("project")
        super(TagTool, self).__init__(**kwargs)

    @property
    def linkable_resources(self):
        """``Resources`` that could be linked to this ``Tag``"""
        return self.resource_tool.get_linkable_resources(self.slug)

    @property
    def linked_resources(self):
        """``Resources`` that are linked to this ``Tag``"""
        return self.resource_tool.get_linked_resources(self.slug)

    @property
    def name(self):
        """Name of ``Tag`` model object"""
        return self._name

    @property
    def pk(self):
        """PK of ``Tag`` model object"""
        return self._pk

    @property
    def priority(self):
        """Priority of ``Tag`` model object"""
        return self._priority

    @property
    def project(self):
        """``Project`` pk (if set) of ``Tag`` model object"""
        return self._project

    @property
    def slug(self):
        """Slug of ``Tag`` model object"""
        return self._slug

    @cached_property
    def locale_latest(self):
        """A cached property containing latest locale changes
        """
        return self.tags_tool.translation_tool(
            slug=self.slug,
            groupby='locale').data

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
            else self.tags_tool.resource_tool)

    def link_resources(self, resources):
        """Link Resources to this tag, raises an Error if the tag's
        Project is set, and the requested resource is not in  that Project
        """
        return self.resource_tool.link(self.slug, resources=resources)

    def unlink_resources(self, resources):
        """Unlink Resources from this tag
        """
        return self.resource_tool.unlink(self.slug, resources=resources)

    @cached_property
    def object(self):
        """Returns the ``Tag`` model object for this tag.
        This is useful for introspection, but should be avoided in
        actual code
        """
        return self.tags_tool.tag_manager.select_related('project').get(pk=self.pk)

    @property
    def locale_stats(self):
        return self.tags_tool.stat_tool(
            slug=self.slug,
            groupby='locale').data

    def iter_locales(self, project=None):
        """Iterate ``Locales`` that are associated with this tag
        (given any filtering in ``self.tags_tool``)

        yields a ``TaggedLocale`` that can be used to get eg chart data
        """
        for locale in self.locale_stats:
            yield TaggedLocale(
                project=project,
                latest_translation=self.locale_latest.get(locale["locale"]),
                **locale)

    def url(self, project=None, locale=None):
        if locale and project:
            return reverse(
                'pontoon.localizations.tags.tag',
                kwargs=dict(
                    code=locale.code,
                    slug=project.slug,
                    tag=self.slug))
        elif project:
            return reverse(
                'pontoon.tags.project.tag',
                kwargs=dict(
                    project=project.slug,
                    tag=self.slug))
        else:
            return ""
