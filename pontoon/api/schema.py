import graphene
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug

from .util import get_fields

from ..base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel
)


class Items(graphene.AbstractType):
    total_count = graphene.Int()


class ProjectLocale(DjangoObjectType):
    class Meta:
        model = ProjectLocaleModel
        only_fields = (
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings', 'project', 'locale')


class ProjectLocaleItems(graphene.ObjectType, Items):
    items = graphene.List(ProjectLocale)


class Project(DjangoObjectType):
    class Meta:
        model = ProjectModel
        only_fields = (
            'name', 'slug', 'info', 'deadline', 'priority', 'contact',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings')

    locales = graphene.Field(ProjectLocaleItems)

    @graphene.resolve_only_args
    def resolve_locales(self):
        qs = self.project_locale.all()
        return ProjectLocaleItems(
            total_count=qs.count(),
            items=qs
        )


class ProjectItems(graphene.ObjectType, Items):
    items = graphene.List(Project)


class Locale(DjangoObjectType):
    class Meta:
        model = LocaleModel
        only_fields = (
            'name', 'code', 'direction', 'script', 'population',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings')

    projects = graphene.Field(ProjectLocaleItems)

    @graphene.resolve_only_args
    def resolve_projects(self):
        qs = self.project_locale.all()
        return ProjectLocaleItems(
            total_count=qs.count(),
            items=qs
        )


class LocaleItems(graphene.ObjectType, Items):
    items = graphene.List(Locale)


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')

    projects = graphene.Field(ProjectItems)
    project = graphene.Field(Project, slug=graphene.String())

    locales = graphene.Field(LocaleItems)
    locale = graphene.Field(Locale, code=graphene.String())

    def resolve_projects(self, args, context, info):
        qs = ProjectModel.objects.all()
        fields = get_fields(info)

        if 'projects.items.locales' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'projects.items.locales.items.locale.projects' in fields:
            raise Exception('Cyclic queries are forbidden')

        return ProjectItems(
            total_count=qs.count(),
            items=qs
        )

    def resolve_project(self, args, context, info):
        qs = ProjectModel.objects
        fields = get_fields(info)

        if 'project.locales' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'project.locales.items.locale.projects' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(slug=args['slug'])

    def resolve_locales(self, args, context, info):
        qs = LocaleModel.objects.all()
        fields = get_fields(info)

        if 'locales.items.projects' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locales.items.projects.items.project.locales' in fields:
            raise Exception('Cyclic queries are forbidden')

        return LocaleItems(
            total_count=qs.count(),
            items=qs
        )

    def resolve_locale(self, args, context, info):
        qs = LocaleModel.objects
        fields = get_fields(info)

        if 'locale.projects' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locale.projects.items.project.locales' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(code=args['code'])


schema = graphene.Schema(query=Query)
