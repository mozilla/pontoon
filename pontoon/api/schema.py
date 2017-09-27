import graphene
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug

from pontoon.api.util import get_fields

from pontoon.base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel
)


class Stats(graphene.AbstractType):
    missing_strings = graphene.Int()
    complete = graphene.Boolean()


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
            'name', 'slug', 'disabled', 'info', 'deadline', 'priority',
            'contact', 'total_strings', 'approved_strings',
            'translated_strings', 'fuzzy_strings'
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

    # include_disabled=True will return both active and disabled projects.
    projects = graphene.List(Project, include_disabled=graphene.Boolean(False))
    project = graphene.Field(Project, slug=graphene.String())

    locales = graphene.List(Locale)
    locale = graphene.Field(Locale, code=graphene.String())

    def resolve_projects(obj, args, context, info):
        qs = ProjectModel.objects
        fields = get_fields(info)

        if 'projects.localizations' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'projects.localizations.locale.localizations' in fields:
            raise Exception('Cyclic queries are forbidden')

        if args['include_disabled']:
            return qs.all()

        return qs.filter(disabled=False)

    def resolve_project(obj, args, context, info):
        qs = ProjectModel.objects
        fields = get_fields(info)

        if 'project.localizations' in fields:
            qs = qs.prefetch_related('project_locale__locale')

        if 'project.localizations.locale.localizations' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(slug=args['slug'])

    def resolve_locales(obj, args, context, info):
        qs = LocaleModel.objects
        fields = get_fields(info)

        if 'locales.localizations' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locales.localizations.project.localizations' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.all()

    def resolve_locale(obj, args, context, info):
        qs = LocaleModel.objects
        fields = get_fields(info)

        if 'locale.localizations' in fields:
            qs = qs.prefetch_related('project_locale__project')

        if 'locale.localizations.project.localizations' in fields:
            raise Exception('Cyclic queries are forbidden')

        return qs.get(code=args['code'])


schema = graphene.Schema(query=Query)
