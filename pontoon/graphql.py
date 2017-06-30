import graphene
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .base.models import (
    Project as ProjectModel,
    Locale as LocaleModel,
    ProjectLocale as ProjectLocaleModel,
    Entity as EntityModel,
    Translation as TranslationModel
)


class PageInfo(graphene.ObjectType):
    page_size = graphene.Int()
    page_number = graphene.Int()
    has_next = graphene.Boolean()
    has_previous = graphene.Boolean()


class Page(graphene.AbstractType):
    total_count = graphene.Int()
    page_info = graphene.Field(PageInfo)


class Localization(DjangoObjectType):
    class Meta:
        model = ProjectLocaleModel


class LocalizationPage(graphene.ObjectType, Page):
    edges = graphene.List(Localization)


class Project(DjangoObjectType):
    class Meta:
        model = ProjectModel

    localizations = graphene.Field(LocalizationPage, page=graphene.Int())

    @graphene.resolve_only_args
    def resolve_localizations(self, page=1):
        return get_page(LocalizationPage, self.project_locale.all(), page)


class ProjectPage(graphene.ObjectType, Page):
    edges = graphene.List(Project)


class Locale(DjangoObjectType):
    class Meta:
        model = LocaleModel

    localizations = graphene.Field(LocalizationPage, page=graphene.Int())

    @graphene.resolve_only_args
    def resolve_localizations(self, page=1):
        return get_page(LocalizationPage, self.project_locale.all(), page)


class LocalePage(graphene.ObjectType, Page):
    edges = graphene.List(Locale)


class Entity(DjangoObjectType):
    class Meta:
        model = EntityModel


class Translation(DjangoObjectType):
    class Meta:
        model = TranslationModel


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')

    projects = graphene.Field(ProjectPage, page=graphene.Int(default_value=1))
    locales = graphene.Field(LocalePage, page=graphene.Int(default_value=1))
    entities = graphene.List(Entity)
    translations = graphene.List(Translation)

    @graphene.resolve_only_args
    def resolve_projects(self, page):
        return get_page(ProjectPage, ProjectModel.objects.all(), page)

    @graphene.resolve_only_args
    def resolve_locales(self, page):
        return get_page(LocalePage, LocaleModel.objects.all(), page)

    @graphene.resolve_only_args
    def resolve_entities(self):
        return EntityModel.objects.all()

    @graphene.resolve_only_args
    def resolve_translations(self):
        return TranslationModel.objects.prefetch_related('entity').all()


def get_page(shape, queryset, page):
    paginator = Paginator(queryset, 10)

    try:
        edges = paginator.page(page)
    except PageNotAnInteger:
        edges = paginator.page(1)
    except EmptyPage:
        edges = []

    page_info = PageInfo(
        page_size=10,
        page_number=page,
        has_next=edges.has_next(),
        has_previous=edges.has_previous())

    return shape(
        total_count=paginator.count,
        edges=edges,
        page_info=page_info)


schema = graphene.Schema(query=Query)
