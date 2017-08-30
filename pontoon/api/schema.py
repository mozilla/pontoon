import graphene
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug

from .util import get_fields

from ..base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel
)


class Stats(graphene.AbstractType):
    missing_strings = graphene.Int()

    @graphene.resolve_only_args
    def resolve_missing_strings(obj):
        return (
            obj.total_strings - obj.translated_strings -
            obj.approved_strings - obj.fuzzy_strings
        )


class ProjectLocale(DjangoObjectType, Stats):
    class Meta:
        model = ProjectLocaleModel
        only_fields = (
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings', 'project', 'locale'
        )


class Project(DjangoObjectType, Stats):
    class Meta:
        model = ProjectModel
        only_fields = (
            'name', 'slug', 'info', 'deadline', 'priority', 'contact',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings'
        )

    localizations = graphene.List(ProjectLocale)

    @graphene.resolve_only_args
    def resolve_localizations(obj):
        return obj.project_locale.all()


class Locale(DjangoObjectType, Stats):
    class Meta:
        model = LocaleModel
        only_fields = (
            'name', 'code', 'direction', 'script', 'population',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings'
        )

    localizations = graphene.List(ProjectLocale)

    @graphene.resolve_only_args
    def resolve_localizations(obj):
        return obj.project_locale.all()


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')

    projects = graphene.List(Project)
    project = graphene.Field(Project, slug=graphene.String())

    locales = graphene.List(Project)
    locale = graphene.Field(Locale, code=graphene.String())

    def resolve_projects(obj, args, context, info):
        qs = ProjectModel.objects.all()
        fields = get_fields(info)

        if 'projects.localizations' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'projects.localizations.locale.localizations' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs

    def resolve_project(obj, args, context, info):
        qs = ProjectModel.objects
        fields = get_fields(info)

        if 'project.localizations' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'project.localizations.locale.localizations' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(slug=args['slug'])

    def resolve_locales(obj, args, context, info):
        qs = LocaleModel.objects.all()
        fields = get_fields(info)

        if 'locales.localizations' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locales.localizations.project.localizations' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs

    def resolve_locale(obj, args, context, info):
        qs = LocaleModel.objects
        fields = get_fields(info)

        if 'locale.localizations' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locale.localizations.project.localizations' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(code=args['code'])


schema = graphene.Schema(query=Query)
