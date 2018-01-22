
import math
from collections import OrderedDict

from django.urls import reverse
from django.utils.functional import cached_property
from django.db.models import F, Max, Sum, Value
from django.db.models.functions import Coalesce

from pontoon.base.models import (
    Locale, Project, Resource, Translation, TranslatedResource)
from pontoon.base.utils import glob_to_regex

from .exceptions import InvalidProjectError
from .models import Tag


class TagChart(object):

    def __init__(self, **kwargs):
        self.approved_strings = kwargs['approved_strings']
        self.fuzzy_strings = kwargs['fuzzy_strings']
        self.total_strings = kwargs['total_strings']
        self.translated_strings = kwargs['translated_strings']

    @property
    def approved_percent(self):
        return int(
            math.floor(
                self.approved_strings
                / float(self.total_strings) * 100))

    @property
    def approved_share(self):
        return self._share(self.approved_strings)

    @property
    def fuzzy_share(self):
        return self._share(self.fuzzy_strings)

    @property
    def translated_share(self):
        return self._share(self.translated_strings)

    def _share(self, item):
        return round(item / float(self.total_strings) * 100)


class Tagged(object):

    def __init__(self, **kwargs):
        self._latest_translation = kwargs.pop(
            "latest_translation", None)
        self.approved_strings = kwargs.get('approved_strings')
        self.fuzzy_strings = kwargs.get('fuzzy_strings')
        self.total_strings = kwargs.get('total_strings')
        self.translated_strings = kwargs.get('translated_strings')
        self.kwargs = kwargs

    @property
    def chart(self):
        return (
            TagChart(**self.kwargs)
            if self.kwargs.get('total_strings')
            else None)

    @property
    def latest_translation(self):
        return self._latest_translation

    @property
    def latest_activity(self):
        return (
            self.latest_translation.latest_activity
            if self.latest_translation
            else None)

    @property
    def tag(self):
        return self.kwargs.get('slug')


class TaggedResource(Tagged):

    @property
    def title(self):
        return self.path

    @property
    def path(self):
        return self.kwargs.get('path')

    @property
    def project(self):
        return self.kwargs.get('project')


class TaggedLocale(Tagged):

    @property
    def code(self):
        return self.kwargs.get('locale_code')

    @property
    def name(self):
        return self.kwargs.get('locale_name')


class TaggedProject(Tagged):

    @property
    def slug(self):
        return self.kwargs.get('project_slug')

    @property
    def name(self):
        return self.kwargs.get('project_name')

    @property
    def deadline(self):
        return self.kwargs.get('project_deadline')

    @property
    def priority(self):
        return self.kwargs.get('project_priority')


class TagTool(Tagged):

    def __init__(self, tags_tool, **kwargs):
        self.tags_tool = tags_tool
        self._name = kwargs.pop("name")
        self._pk = kwargs.pop("pk")
        self._priority = kwargs.pop("priority")
        self._slug = kwargs.pop("slug")
        self._project = kwargs.pop("project")
        super(TagTool, self).__init__(**kwargs)

    @property
    def pk(self):
        """PK of Tag model object"""
        return self._pk

    @property
    def locales(self):
        """List of Locales that this Tag is active in"""
        return Locale.objects.filter(
            pk__in=self.resources.values_list(
                "translatedresources__locale").distinct())

    @property
    def name(self):
        """Name of Tag model object"""
        return self._name

    @property
    def priority(self):
        """Priority of Tag model object"""
        return self._priority

    @property
    def project(self):
        """Project (if set) of Tag model object"""
        return self._project

    @property
    def projects(self):
        """Projects that this TagTool will provide information about"""
        return Project.objects.filter(
            pk__in=self.resources.values_list(
                "project").distinct())

    @property
    def addable_resources(self):
        """Resources that could be linked to this Tag"""
        tool = (
            self.tags_tool(projects=[self.project])
            if self.project
            else self.tags_tool)
        result = tool.resource_tool.find('*', exclude=self.slug)
        return result.values('path', 'project')

    @property
    def resources(self):
        return self.tags_tool.resource_tool.get(self.slug)

    @property
    def slug(self):
        return self._slug

    @cached_property
    def locale_stats(self):
        return self.get_locale_stats().stat_tool.data

    @cached_property
    def project_stats(self):
        return self.get_project_stats().stat_tool.data

    @cached_property
    def resource_stats(self):
        return self.get_resource_stats().stat_tool.data

    def add_resources(self, resources):
        _resources = Resource.objects.none()
        for resource in resources:
            if self.project and resource["project"] != self.project:
                raise InvalidProjectError(
                    "Cannot add Resource from Project (%s) to Tag (%s)"
                    % (self.project, self.slug))
            _resources |= Resource.objects.filter(
                project=resource["project"],
                path=resource["path"])
        self.get_object().resources.add(*list(_resources))

    def remove_resources(self, resources):
        _resources = Resource.objects.none()
        for resource in resources:
            if self.project and resource["project"] != self.project:
                raise InvalidProjectError(
                    "Cannot add Resource from Project (%s) to Tag (%s)"
                    % (self.project, self.slug))
            _resources |= Resource.objects.filter(
                project=resource["project"],
                path=resource["path"])
        self.get_object().resources.remove(*list(_resources))

    def get_object(self):
        return Tag.objects.get(pk=self.pk)

    def get_locale_stats(self):
        return self.tags_tool(
            slug=self.slug,
            groupby=["locale"],
            annotations=dict(
                locale_code=F("locale__code"),
                locale_name=F("locale__name")))

    def get_project_stats(self):
        return self.tags_tool(
            slug=self.slug,
            groupby=["resource__project"],
            annotations=dict(
                project_slug=F("resource__project__slug"),
                project_name=F("resource__project__name"),
                project_deadline=F("resource__project__deadline"),
                project_priority=F("resource__project__priority")))

    def get_resource_stats(self):
        return self.tags_tool(
            slug=self.slug,
            groupby=["resource"],
            annotations=dict(
                project_slug=F("resource__project__slug"),
                path=F("resource__path")))

    def iter_locales(self):
        for locale in self.locale_stats:
            yield TaggedLocale(**locale)

    def iter_projects(self):
        for project in self.project_stats:
            yield TaggedProject(**project)

    def iter_resources(self, addable=False, associated=True):
        if addable:
            for resource in self.addable_resources:
                yield TaggedResource(**resource)
        if associated:
            for resource in self.resource_stats:
                yield TaggedResource(**resource)

    def iter_resource_paths(self):
        return self.resources.values_list(
            "project__slug", "path").distinct().iterator()

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
                'pontoon.projects.tags.tag',
                kwargs=dict(
                    slug=project.slug,
                    tag=self.slug))
        else:
            return ""


class TagsModelTool(object):
    _filters = (
        'empty', 'locales', 'projects', 'priority', 'slug', 'path')

    def __init__(self, slug=None, locales=None, projects=None,
                 priority=None, path=None):
        self.locales = locales
        self.projects = projects
        self.priority = priority
        self.slug = slug
        self.path = path

    @property
    def filters(self):
        return [
            getattr(self, "filter_%s" % f)
            for f
            in self._filters]

    def filter_empty(self, trs):
        return (
            trs.exclude(resource__tag__isnull=True)
            if not self.slug
            else trs)

    def filter_locales(self, trs):
        return (
            trs.filter(locale__in=self.locales)
            if self.locales
            else trs)

    def filter_path(self, trs):
        return (
            trs.filter(
                resource__path__regex=glob_to_regex(self.path))
            if self.path
            else trs)

    def filter_priority(self, trs):
        if self.priority is not None:
            if self.priority is False:
                # if priority is False, exclude tags with priority
                trs = trs.filter(resource__tag__priority__isnull=True)
            elif self.priority is True:
                # if priority is True show only tags with priority
                trs = trs.filter(resource__tag__priority__isnull=False)
            elif isinstance(self.priority, int):
                # if priority is an int, filter on that priority
                trs = trs.filter(resource__tag__priority=self.priority)
        return trs

    def filter_projects(self, trs):
        return (
            trs.filter(resource__project__in=self.projects)
            if self.projects
            else trs)

    def filter_slug(self, trs):
        return (
            trs.filter(resource__tag__slug__regex=glob_to_regex(self.slug))
            if self.slug
            else trs)


class TagsResourcesTool(TagsModelTool):

    _filters = ('locales', 'projects', 'slug', 'path')

    @property
    def resource_manager(self):
        return Resource.objects

    @property
    def resources(self):
        resources = self.resource_manager.all()
        for tag_filter in self.filters:
            resources = tag_filter(resources)
        return resources

    @property
    def tag_manager(self):
        return Tag.objects

    def add(self, tag, glob):
        resources = list(self.find(glob, exclude=tag))
        self.tag_manager.get(slug=tag).resources.add(*resources)
        return resources

    def filter_locales(self, resources):
        return (
            resources.filter(translatedresources__locale__in=self.locales)
            if self.locales
            else resources)

    def filter_path(self, resources):
        return (
            resources.filter(path__regex=glob_to_regex(self.path))
            if self.path
            else resources)

    def filter_projects(self, resources):
        return (
            resources.filter(project__in=self.projects)
            if self.projects
            else resources)

    def filter_slug(self, resources):
        return (
            resources.filter(tag__slug__regex=glob_to_regex(self.slug))
            if self.slug
            else resources)

    def find(self, glob, include=None, exclude=None):
        if include:
            resources = self.resource_manager.filter(tag__slug=include)
        elif exclude:
            resources = self.resource_manager.exclude(tag__slug=exclude)
        else:
            resources = self.resource_manager
        if self.projects:
            resources = resources.filter(project__in=self.projects)
        return resources.filter(path__regex=glob_to_regex(glob))

    def get(self, tag):
        return self.resources.filter(tag__slug=tag).distinct()

    def remove(self, tag, glob):
        resources = list(self.find(glob, include=tag))
        self.tag_manager.get(slug=tag).resources.remove(*resources)
        return resources


class TagsStatsTool(TagsModelTool):

    # from the perspective of translated resources
    _default_annotations = (
        ('name', F("resource__tag__name")),
        ('slug', F("resource__tag__slug")),
        ('priority', F("resource__tag__priority")),
        ('project', F("resource__tag__project")),
        # ('last_change', Max("latest_translation__date")),
        ('total_strings', Coalesce(
            Sum('resource__total_strings'),
            Value(0))),
        ('fuzzy_strings', Coalesce(
            Sum("fuzzy_strings"),
            Value(0))),
        ('approved_strings', Coalesce(
            Sum("approved_strings"),
            Value(0))),
        ('translated_strings', Coalesce(
            Sum("translated_strings"),
            Value(0))))

    def __init__(self, **kwargs):
        self._annotations = kwargs.pop('annotations', None) or {}
        self._groupby = kwargs.pop('groupby', None) or []
        super(TagsStatsTool, self).__init__(**kwargs)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    @property
    def annotations(self):
        anno = self._annotations.copy()
        anno.update(self.default_annotations)
        return anno

    @property
    def default_annotations(self):
        return OrderedDict(self._default_annotations)

    @property
    def groupby(self):
        return ["pk"] + self._groupby

    @property
    def tag_trs(self):
        return self.trs.annotate(pk=F("resource__tag"))

    @property
    def tr_manager(self):
        return TranslatedResource.objects

    @property
    def trs(self):
        trs = self.tr_manager.all()
        for tag_filter in self.filters:
            trs = tag_filter(trs)
        return trs

    @cached_property
    def data(self):
        return list(self.get_data())

    def get_data(self):
        data = self.tag_trs.order_by(
            *self.groupby).values(
                *self.groupby).annotate(**self.annotations)
        return (
            data.filter(slug__regex=glob_to_regex(self.slug))
            if self.slug
            else data)


class TagsTranslationsTool(TagsModelTool):

    @property
    def translation_manager(self):
        return Translation.objects

    @property
    def tr_manager(self):
        return TranslatedResource.objects

    @property
    def trs(self):
        trs = self.tr_manager.all()
        for tag_filter in self.filters:
            trs = tag_filter(trs)
        return trs

    @cached_property
    def last_changes(self):
        return list(self.get_last_changes())

    @cached_property
    def latest(self):
        return self.get_latest()

    def filter_translation_dates(self, qs):
        translations = self.translation_manager.none()
        tag_dates = (
            (stat['pk'], stat['last_change'])
            for stat
            in self.last_changes)
        for tag, date in tag_dates:
            translations |= qs.filter(
                date=date,
                resource_latest__resource__tag__pk=tag)
        return translations

    def get_last_changes(self):
        return self.trs.exclude(
            latest_translation__isnull=True).annotate(
                pk=F("resource__tag__pk")).values('pk').annotate(
                    last_change=Max('latest_translation__date'))

    def get_latest(self):
        qs = self.filter_translation_dates(self.translation_manager.all())
        return {
            tr.tag: tr
            for tr
            in qs.annotate(
                tag=F('resource_latest__resource__tag__pk'))}


class TagsTool(object):
    tag_class = TagTool
    resources_class = TagsResourcesTool
    translations_class = TagsTranslationsTool
    stats_class = TagsStatsTool

    def __init__(self, locales=None, projects=None, priority=None,
                 slug=None, path=None, annotations=None, groupby=None):
        self.locales = locales
        self.projects = projects
        self.priority = priority
        self.slug = slug
        self.path = path
        self.groupby = groupby
        self.annotations = annotations

    def __call__(self, **kwargs):
        return self._clone(**kwargs)

    def __getitem__(self, k):
        return self(slug=k)

    def __iter__(self):
        return self.iter_tags(self.stat_tool)

    def __len__(self):
        return len(self.stat_tool)

    @property
    def all_tags(self):
        return self.iter_tags(
            self.tag_manager.values(
                "pk", "name", "slug", "priority", "project"))

    @property
    def empty_tags(self):
        tags = self.get_tags(slug=self.slug).exclude(
            resources__translatedresources__isnull=False).distinct()
        return self.iter_tags(tags)

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
            annotations=self.annotations,
            groupby=self.groupby,
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
            latest_translation = self.translation_tool.latest.get(tag["pk"])
            yield self.tag_class(
                self,
                latest_translation=latest_translation,
                **tag)

    def update(self, slug, k, v):
        tag = self.tag_manager.get(slug=slug)
        setattr(tag, k, v)
        tag.save()

    def _clone(self, **kwargs):
        clone_kwargs = dict(
            (k, getattr(self, k))
            for k
            in ['annotations',
                'groupby',
                'locales',
                'projects',
                'priority',
                'path',
                'slug'])
        clone_kwargs.update(kwargs)
        return self.__class__(**clone_kwargs)
