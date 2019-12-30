from __future__ import absolute_import

import graphene
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug

from pontoon.api.util import get_fields

from pontoon.base.models import (
    Locale as LocaleModel,
    Project as ProjectModel,
    ProjectLocale as ProjectLocaleModel,
)

from pontoon.tags.models import Tag as TagModel


class Stats(object):
    missing_strings = graphene.Int()
    complete = graphene.Boolean()


class Tag(DjangoObjectType):
    class Meta:
        convert_choices_to_enum = False
        model = TagModel
        only_fields = (
            "slug",
            "name",
            "priority",
        )


class ProjectLocale(DjangoObjectType, Stats):
    class Meta:
        model = ProjectLocaleModel
        only_fields = (
            "project",
            "locale",
            "total_strings",
            "approved_strings",
            "fuzzy_strings",
            "strings_with_errors",
            "strings_with_warnings",
            "unreviewed_strings",
        )


class Project(DjangoObjectType, Stats):
    class Meta:
        model = ProjectModel
        only_fields = (
            "name",
            "slug",
            "disabled",
            "sync_disabled",
            "info",
            "deadline",
            "priority",
            "contact",
            "total_strings",
            "approved_strings",
            "fuzzy_strings",
            "strings_with_errors",
            "strings_with_warnings",
            "unreviewed_strings",
        )

    localizations = graphene.List(ProjectLocale)
    tags = graphene.List(Tag)

    def resolve_localizations(obj, _info):
        return obj.project_locale.all()

    def resolve_tags(obj, _info):
        return obj.tag_set.all()


class Locale(DjangoObjectType, Stats):
    class Meta:
        model = LocaleModel
        only_fields = (
            "name",
            "code",
            "direction",
            "cldr_plurals",
            "plural_rule",
            "script",
            "population",
            "total_strings",
            "approved_strings",
            "fuzzy_strings",
            "strings_with_errors",
            "strings_with_warnings",
            "unreviewed_strings",
            "google_translate_code",
            "ms_translator_code",
            "ms_terminology_code",
            "transvision",
        )

    localizations = graphene.List(
        ProjectLocale, include_disabled=graphene.Boolean(False),
    )

    def resolve_localizations(obj, _info, include_disabled):
        qs = obj.project_locale

        if include_disabled:
            return qs.all()

        return qs.filter(project__disabled=False)


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="__debug")

    # include_disabled=True will return both active and disabled projects.
    projects = graphene.List(Project, include_disabled=graphene.Boolean(False))
    project = graphene.Field(Project, slug=graphene.String())

    locales = graphene.List(Locale)
    locale = graphene.Field(Locale, code=graphene.String())

    def resolve_projects(obj, info, include_disabled):
        qs = ProjectModel.objects
        fields = get_fields(info)

        if "projects.localizations" in fields:
            qs = qs.prefetch_related("project_locale__locale")

        if "projects.localizations.locale.localizations" in fields:
            raise Exception("Cyclic queries are forbidden")

        if include_disabled:
            return qs.all()

        return qs.filter(disabled=False)

    def resolve_project(obj, info, slug):
        qs = ProjectModel.objects
        fields = get_fields(info)

        if "project.localizations" in fields:
            qs = qs.prefetch_related("project_locale__locale")

        if "project.tags" in fields:
            qs = qs.prefetch_related("tag_set")

        if "project.localizations.locale.localizations" in fields:
            raise Exception("Cyclic queries are forbidden")

        return qs.get(slug=slug)

    def resolve_locales(obj, info):
        qs = LocaleModel.objects
        fields = get_fields(info)

        if "locales.localizations" in fields:
            qs = qs.prefetch_related("project_locale__project")

        if "locales.localizations.project.localizations" in fields:
            raise Exception("Cyclic queries are forbidden")

        return qs.all()

    def resolve_locale(obj, info, code):
        qs = LocaleModel.objects
        fields = get_fields(info)

        if "locale.localizations" in fields:
            qs = qs.prefetch_related("project_locale__project")

        if "locale.localizations.project.localizations" in fields:
            raise Exception("Cyclic queries are forbidden")

        return qs.get(code=code)


schema = graphene.Schema(query=Query)
