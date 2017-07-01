import graphene
from graphene import relay
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.debug import DjangoDebug

from .base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel,
)


class Project(DjangoObjectType):
    class Meta:
        model = ProjectModel
        interfaces = (relay.Node, )
        only_fields = (
            'name', 'info', 'deadline', 'priority', 'contact',
            'project_locale')

    def resolve_project_locale(root, args, context, info):
        # This seems wrong. It creates a completely new QuerySet which doesn't
        # have access to the prefetch cache of the QuerySet from which root
        # originated.
        # return ProjectLocaleModel.objects.filter(project_id=root.id)

        # XXX Maybe select_related('locale') or prefetch_related('locale')
        return root.project_locale


class Locale(DjangoObjectType):
    class Meta:
        model = LocaleModel
        interfaces = (relay.Node, )
        only_fields = (
            'name', 'code', 'direction', 'script', 'population',
            'project_locale')

    def resolve_project_locale(root, args, context, info):
        # XXX Maybe select_related('project') or prefetch_related('project')
        return root.project_locale


class ProjectLocale(DjangoObjectType):
    class Meta:
        model = ProjectLocaleModel
        interfaces = (relay.Node, )
        only_fields = (
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings', 'project', 'locale')


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')
    node = relay.Node.Field()

    projects = DjangoConnectionField(Project)
    locales = DjangoConnectionField(Locale)

    def resolve_projects(root, args, context, info):
        return ProjectModel.objects.prefetch_related('project_locale__locale')

    def resolve_locales(root, args, context, info):
        return LocaleModel.objects.prefetch_related('project_locale__project')


schema = graphene.Schema(query=Query)
