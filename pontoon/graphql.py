import graphene
from graphene import relay
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.debug import DjangoDebug

from .base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel,
    Entity as EntityModel,
    Translation as TranslationModel
)


class Project(DjangoObjectType):
    class Meta:
        model = ProjectModel
        only_fields = (
            'name', 'info', 'deadline', 'priority', 'contact',
            'project_locale')
        interfaces = (relay.Node, )


class Locale(DjangoObjectType):
    class Meta:
        model = LocaleModel
        interfaces = (relay.Node, )


class Localization(DjangoObjectType):
    class Meta:
        model = ProjectLocaleModel
        interfaces = (relay.Node, )


class Entity(DjangoObjectType):
    class Meta:
        model = EntityModel
        interfaces = (relay.Node, )


class Translation(DjangoObjectType):
    class Meta:
        model = TranslationModel
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')
    node = relay.Node.Field()

    projects = DjangoConnectionField(Project)
    locales = DjangoConnectionField(Locale)
    entities = DjangoConnectionField(Entity)
    translations = DjangoConnectionField(Translation)


schema = graphene.Schema(query=Query)
