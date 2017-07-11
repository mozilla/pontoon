import graphene
from graphene import relay
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.debug import DjangoDebug

from .base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel
)


class ProjectNode(DjangoObjectType):
    class Meta:
        model = ProjectModel
        interfaces = (relay.Node, )
        only_fields = (
            'name', 'info', 'deadline', 'priority', 'contact',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings', 'project_locale', 'resources')


class LocaleNode(DjangoObjectType):
    class Meta:
        model = LocaleModel
        interfaces = (relay.Node, )
        only_fields = (
            'name', 'code', 'direction', 'script', 'population',
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings', 'project_locale')


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


schema = graphene.Schema(query=Query)
