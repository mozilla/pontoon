import graphene
from graphene import relay
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.debug import DjangoDebug

from .base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel,
)


class ProjectNode(DjangoObjectType):
    class Meta:
        model = ProjectModel
        interfaces = (relay.Node, )
        only_fields = (
            'name', 'info', 'deadline', 'priority', 'contact',
            'project_locale')


class LocaleNode(DjangoObjectType):
    class Meta:
        model = LocaleModel
        interfaces = (relay.Node, )
        only_fields = (
            'name', 'code', 'direction', 'script', 'population',
            'project_locale')


class ProjectLocaleNode(DjangoObjectType):
    class Meta:
        model = ProjectLocaleModel
        interfaces = (relay.Node, )
        only_fields = (
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings', 'project', 'locale')


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')
    node = relay.Node.Field()

    project = relay.Node.Field(ProjectNode)
    projects = DjangoConnectionField(ProjectNode)

    locale = relay.Node.Field(LocaleNode)
    locales = DjangoConnectionField(LocaleNode)

    def resolve_projects(root, args, context, info):
        return ProjectModel.objects.prefetch_related('project_locale__locale')

    def resolve_locales(root, args, context, info):
        return LocaleModel.objects.prefetch_related('project_locale__project')


schema = graphene.Schema(query=Query)
