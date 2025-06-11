import graphene

from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug

from django.db.models import Prefetch, Q

from pontoon.api.util import get_fields
from pontoon.base.models import (
    Locale as LocaleModel,
    Project as ProjectModel,
    ProjectLocale as ProjectLocaleModel,
    TranslationMemoryEntry as TranslationMemoryEntryModel,
)
from pontoon.tags.models import Tag as TagModel
from pontoon.terminology.models import (
    Term as TermModel,
    TermTranslation as TermTranslationModel,
)


class Stats:
    missing_strings = graphene.Int()
    complete = graphene.Boolean()


class Tag(DjangoObjectType):
    class Meta:
        convert_choices_to_enum = False
        model = TagModel
        fields = (
            "slug",
            "name",
            "priority",
        )


class ProjectLocale(DjangoObjectType, Stats):
    total_strings = graphene.Int()
    approved_strings = graphene.Int()
    pretranslated_strings = graphene.Int()
    strings_with_errors = graphene.Int()
    strings_with_warnings = graphene.Int()
    unreviewed_strings = graphene.Int()

    class Meta:
        model = ProjectLocaleModel
        fields = (
            "project",
            "locale",
            "total_strings",
            "approved_strings",
            "pretranslated_strings",
            "strings_with_errors",
            "strings_with_warnings",
            "unreviewed_strings",
        )


class Project(DjangoObjectType, Stats):
    total_strings = graphene.Int()
    approved_strings = graphene.Int()
    pretranslated_strings = graphene.Int()
    strings_with_errors = graphene.Int()
    strings_with_warnings = graphene.Int()
    unreviewed_strings = graphene.Int()

    class Meta:
        convert_choices_to_enum = False
        model = ProjectModel
        fields = (
            "name",
            "slug",
            "disabled",
            "sync_disabled",
            "pretranslation_enabled",
            "visibility",
            "system_project",
            "info",
            "deadline",
            "priority",
            "contact",
            "total_strings",
            "approved_strings",
            "pretranslated_strings",
            "strings_with_errors",
            "strings_with_warnings",
            "unreviewed_strings",
        )

    localizations = graphene.List(ProjectLocale)
    tags = graphene.List(Tag)

    def resolve_localizations(obj, info):
        return obj.project_locale.all()

    def resolve_tags(obj, info):
        return obj.tags.all()


class Locale(DjangoObjectType, Stats):
    total_strings = graphene.Int()
    approved_strings = graphene.Int()
    pretranslated_strings = graphene.Int()
    strings_with_errors = graphene.Int()
    strings_with_warnings = graphene.Int()
    unreviewed_strings = graphene.Int()

    class Meta:
        model = LocaleModel
        fields = (
            "name",
            "code",
            "direction",
            "cldr_plurals",
            "plural_rule",
            "script",
            "population",
            "team_description",
            "total_strings",
            "approved_strings",
            "pretranslated_strings",
            "strings_with_errors",
            "strings_with_warnings",
            "unreviewed_strings",
            "google_translate_code",
            "ms_translator_code",
            "systran_translate_code",
            "ms_terminology_code",
        )

    localizations = graphene.List(
        ProjectLocale,
        include_disabled=graphene.Boolean(False),
        include_system=graphene.Boolean(False),
    )

    def resolve_localizations(obj, info, include_disabled, include_system):
        projects = obj.project_locale.visible_for(info.context.user)

        records = projects.filter(
            project__disabled=False, project__system_project=False
        )

        if include_disabled:
            records |= projects.filter(project__disabled=True)

        if include_system:
            records |= projects.filter(project__system_project=True)

        return records.distinct()


class TermTranslation(DjangoObjectType):
    class Meta:
        model = TermTranslationModel
        fields = ("text", "locale")


class Term(DjangoObjectType):
    class Meta:
        model = TermModel
        fields = (
            "text",
            "part_of_speech",
            "definition",
            "usage",
        )

    translations = graphene.List(TermTranslation)
    translation_text = graphene.String()

    def resolve_translations(self, info):
        return self.translations.all()

    def resolve_translation_text(self, info):
        # Returns the text of the translation for the specified locale, if available.
        if hasattr(self, "locale_translations") and self.locale_translations:
            return self.locale_translations[0].text
        return None


class TranslationMemoryEntry(DjangoObjectType):
    class Meta:
        model = TranslationMemoryEntryModel
        fields = (
            "source",
            "target",
            "locale",
            "project",
        )


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="_debug")

    # include_disabled=True will return both active and disabled projects.
    # include_system=True will return both system and non-system projects.
    projects = graphene.List(
        Project,
        include_disabled=graphene.Boolean(False),
        include_system=graphene.Boolean(False),
    )
    project = graphene.Field(Project, slug=graphene.String())

    locales = graphene.List(Locale)
    locale = graphene.Field(Locale, code=graphene.String())

    term_search = graphene.List(
        Term,
        search=graphene.String(required=True),
        locale=graphene.String(required=True),
    )

    tm_search = graphene.List(
        TranslationMemoryEntry,
        search=graphene.String(required=True),
        locale=graphene.String(required=True),
    )

    def resolve_projects(obj, info, include_disabled, include_system):
        fields = get_fields(info)

        projects = ProjectModel.objects.visible_for(info.context.user)
        records = projects.filter(disabled=False, system_project=False)

        if include_disabled:
            records |= projects.filter(disabled=True)

        if include_system:
            records |= projects.filter(system_project=True)

        if "projects.localizations" in fields:
            records = records.prefetch_related("project_locale__locale")

        if "projects.localizations.locale.localizations" in fields:
            raise Exception("Cyclic queries are forbidden")

        return records.distinct()

    def resolve_project(obj, info, slug):
        qs = ProjectModel.objects.visible_for(info.context.user)
        fields = get_fields(info)

        if "project.localizations" in fields:
            qs = qs.prefetch_related("project_locale__locale")

        if "project.tags" in fields:
            qs = qs.prefetch_related("tags")

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

    def resolve_term_search(self, info, search, locale):
        term_query = Q(text__icontains=search)

        translation_query = Q(translations__text__icontains=search) & Q(
            translations__locale__code=locale
        )

        # Prefetch translations for the specified locale
        prefetch_translations = Prefetch(
            "translations",
            queryset=TermTranslationModel.objects.filter(locale__code=locale),
            to_attr="locale_translations",
        )

        # Perform the query on the Term model and prefetch translations
        return (
            TermModel.objects.filter(term_query | translation_query)
            .prefetch_related(prefetch_translations)
            .distinct()
        )

    def resolve_tm_search(self, info, search, locale):
        return (
            TranslationMemoryEntryModel.objects.filter(
                Q(Q(source__icontains=search) | Q(target__icontains=search)),
                locale__code=locale,
            )
            .prefetch_related("project")
            .distinct()
        )


schema = graphene.Schema(query=Query)
