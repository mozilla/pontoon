import graphene
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug

from .util import get_fields

from ..base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel
)


class ProjectLocale(DjangoObjectType):
    class Meta:
        model = ProjectLocaleModel
        only_fields = (
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings', 'project', 'locale')


class Project(DjangoObjectType):
    class Meta:
        model = ProjectModel
        only_fields = (
            'name', 'slug', 'info', 'deadline', 'priority', 'contact',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings')

    locales = graphene.List(ProjectLocale)

    @graphene.resolve_only_args
    def resolve_locales(self):
        return self.project_locale.all()


class Locale(DjangoObjectType):
    class Meta:
        model = LocaleModel
        only_fields = (
            'name', 'code', 'direction', 'script', 'population',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings')

    projects = graphene.List(ProjectLocale)

    @graphene.resolve_only_args
    def resolve_projects(self):
        return self.project_locale.all()


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')

    projects = graphene.List(Project)
    project = graphene.Field(Project, slug=graphene.String())

    locales = graphene.List(Project)
    locale = graphene.Field(Locale, code=graphene.String())

    def resolve_projects(self, args, context, info):
        qs = ProjectModel.objects.all()
        fields = get_fields(info)

        if 'projects.locales' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'projects.locales.locale.projects' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs

    def resolve_project(self, args, context, info):
        qs = ProjectModel.objects
        fields = get_fields(info)

        if 'project.locales' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'project.locales.locale.projects' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(slug=args['slug'])

    def resolve_locales(self, args, context, info):
        qs = LocaleModel.objects.all()
        fields = get_fields(info)

        if 'locales.projects' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locales.projects.project.locales' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs

    def resolve_locale(self, args, context, info):
        qs = LocaleModel.objects
        fields = get_fields(info)

        if 'locale.projects' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locale.projects.project.locales' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(code=args['code'])


schema = graphene.Schema(query=Query)
