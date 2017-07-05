import graphene
from graphene import relay
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.debug import DjangoDebug

from .base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel,
    Resource as ResourceModel,
    Entity as EntityModel,
    Translation as TranslationModel,
    TranslatedResource as TranslatedResourceModel
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


class ResourceNode(DjangoObjectType):
    class Meta:
        model = ResourceModel
        interfaces = (relay.Node, )
        only_fields = (
            'path', 'total_strings', 'format', 'deadline', 'priority',
            'project', 'entities')


class TranslatedResourceNode(DjangoObjectType):
    class Meta:
        model = TranslatedResourceModel
        interfaces = (relay.Node, )
        only_fields = (
            'total_strings', 'approved_strings', 'translated_strings',
            'fuzzy_strings', 'project', 'resource', 'locale')


class EntityNode(DjangoObjectType):
    class Meta:
        model = EntityModel
        interfaces = (relay.Node, )
        only_fields = (
            'string', 'string_plural', 'key', 'comment', 'date_created',
            'order', 'source', 'obsolete', 'resource', 'translations')


class TranslationNode(DjangoObjectType):
    class Meta:
        model = TranslationModel
        interfaces = (relay.Node, )
        only_fields = (
            'entity', 'locale', 'string', 'plural_form', 'date', 'approved',
            'approved_date', 'unapproved_date', 'fuzzy', 'extra')


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')
    node = relay.Node.Field()

    project = relay.Node.Field(ProjectNode)
    projects = DjangoConnectionField(ProjectNode)

    locale = relay.Node.Field(LocaleNode)
    locales = DjangoConnectionField(LocaleNode)

    entity = relay.Node.Field(EntityNode)
    entities = DjangoConnectionField(EntityNode)

    translation = relay.Node.Field(TranslationNode)
    translations = DjangoConnectionField(TranslationNode)


schema = graphene.Schema(query=Query)
