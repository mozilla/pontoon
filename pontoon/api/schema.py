from __future__ import absolute_import

from django.contrib.auth.models import User as UserModel

import graphene
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug

from pontoon.api.util import get_fields

from pontoon.actionlog.models import ActionLog as ActionLogModel
from pontoon.base.models import (
    Locale as LocaleModel,
    Project as ProjectModel,
    ProjectLocale as ProjectLocaleModel,
    Translation as TranslationModel,
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


class ActionLog(DjangoObjectType):
    class Meta:
        model = ActionLogModel
        only_fields = (
            "action_type",
            "created_at",
            "performed_by",
            "translation",
        )


class User(DjangoObjectType):
    class Meta:
        convert_choices_to_enum = False
        model = UserModel
        only_fields = (
            "username",
            "first_name",
            "last_name",
        )

    actions = graphene.List(ActionLog)

    def resolve_actions(obj, info):
        return ActionLogModel.objects.filter(performed_by=obj)


class Translation(DjangoObjectType):
    class Meta:
        model = TranslationModel
        only_fields = (
            "user",
            "locale",
            "string",
            "plural_form",
            "date",
            "active",
            "fuzzy",
            "approved",
            "rejected",
        )

    actions = graphene.List(ActionLog)

    def resolve_actions(obj, info):
        return ActionLogModel.objects.filter(translation=obj)


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="__debug")

    # include_disabled=True will return both active and disabled projects.
    projects = graphene.List(Project, include_disabled=graphene.Boolean(False))
    project = graphene.Field(Project, slug=graphene.String())

    locales = graphene.List(Locale)
    locale = graphene.Field(Locale, code=graphene.String())

    user = graphene.Field(User, username=graphene.String())

    translations = graphene.List(
        Translation, project=graphene.String(), locale=graphene.String(),
    )

    actions = graphene.List(ActionLog)

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

    def resolve_user(obj, info, username):
        return UserModel.objects.get(username=username)

    def resolve_translations(obj, info, project, locale):
        qs = TranslationModel.objects
        fields = get_fields(info)

        if "user" in fields:
            qs = qs.prefetch_related("translation__user")

        if "locale" in fields:
            qs = qs.prefetch_related("translation__locale")

        return qs.filter(locale__code=locale, entity__resource__project__slug=project,)

    def resolve_actions(obj, info):
        return ActionLogModel.objects.all()


schema = graphene.Schema(query=Query)
