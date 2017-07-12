import graphene
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .util import get_fields

from ..base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel
)


class PageInfo(graphene.ObjectType):
    page_size = graphene.Int()
    page_number = graphene.Int()
    has_next = graphene.Boolean()
    has_previous = graphene.Boolean()


class Page(graphene.AbstractType):
    total_count = graphene.Int()
    page_info = graphene.Field(PageInfo)


class ProjectLocale(DjangoObjectType):
    class Meta:
        model = ProjectLocaleModel
        only_fields = (
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings', 'project', 'locale')


class ProjectLocalePage(graphene.ObjectType, Page):
    items = graphene.List(ProjectLocale)


class Project(DjangoObjectType):
    class Meta:
        model = ProjectModel
        only_fields = (
            'name', 'info', 'deadline', 'priority', 'contact',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings')

    locales = graphene.Field(ProjectLocalePage, page=graphene.Int())

    @graphene.resolve_only_args
    def resolve_locales(self, page=1):
        return get_page(ProjectLocalePage, self.project_locale.all(), page)


class ProjectPage(graphene.ObjectType, Page):
    items = graphene.List(Project)


class Locale(DjangoObjectType):
    class Meta:
        model = LocaleModel
        only_fields = (
            'name', 'code', 'direction', 'script', 'population',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings')

    projects = graphene.Field(ProjectLocalePage, page=graphene.Int())

    @graphene.resolve_only_args
    def resolve_projects(self, page=1):
        return get_page(ProjectLocalePage, self.project_locale.all(), page)


class LocalePage(graphene.ObjectType, Page):
    items = graphene.List(Locale)


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')

    projects = graphene.Field(ProjectPage, page=graphene.Int(default_value=1))
    project = graphene.Field(Project, pk=graphene.Int())

    locales = graphene.Field(LocalePage, page=graphene.Int(default_value=1))
    locale = graphene.Field(Locale, pk=graphene.Int())

    def resolve_projects(self, args, context, info):
        qs = ProjectModel.objects.all()
        fields = get_fields(info)

        if 'projects.items.locales' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'projects.items.locales.items.locale.projects' in fields:
            raise Exception('Cyclic queries are forbidden')

        return get_page(ProjectPage, qs, args['page'])

    def resolve_project(self, args, context, info):
        qs = ProjectModel.objects
        fields = get_fields(info)

        if 'project.locales' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'project.locales.items.locale.projects' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(pk=args['pk'])

    def resolve_locales(self, args, context, info):
        qs = LocaleModel.objects.all()
        fields = get_fields(info)

        if 'locales.items.projects' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locales.items.projects.items.project.locales' in fields:
            raise Exception('Cyclic queries are forbidden')

        return get_page(LocalePage, qs, args['page'])

    def resolve_locale(self, args, context, info):
        qs = LocaleModel.objects
        fields = get_fields(info)

        if 'locale.projects' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locale.projects.items.project.locales' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(pk=args['pk'])


def get_page(shape, queryset, page):
    paginator = Paginator(queryset, 10)

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = []

    page_info = PageInfo(
        page_size=10,
        page_number=page,
        has_next=items.has_next(),
        has_previous=items.has_previous())

    return shape(
        total_count=paginator.count,
        items=items,
        page_info=page_info)


schema = graphene.Schema(query=Query)
