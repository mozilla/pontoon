from rest_framework import serializers

from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    TranslationMemoryEntry,
)
from pontoon.tags.models import Tag
from pontoon.terminology.models import (
    Term,
)


TRANSLATION_STATS_FIELDS = [
    "total_strings",
    "approved_strings",
    "pretranslated_strings",
    "strings_with_warnings",
    "strings_with_errors",
    "missing_strings",
    "unreviewed_strings",
    "complete",
]


# DO NOT REMOVE serializers.SerializerMetaclass, it is required for serializer functionality
class TranslationStatsMixin(metaclass=serializers.SerializerMetaclass):
    total_strings = serializers.SerializerMethodField()
    approved_strings = serializers.SerializerMethodField()
    pretranslated_strings = serializers.SerializerMethodField()
    strings_with_warnings = serializers.SerializerMethodField()
    strings_with_errors = serializers.SerializerMethodField()
    missing_strings = serializers.SerializerMethodField()
    unreviewed_strings = serializers.SerializerMethodField()
    complete = serializers.SerializerMethodField()

    def get_total_strings(self, obj):
        return obj.total

    def get_approved_strings(self, obj):
        return obj.approved

    def get_pretranslated_strings(self, obj):
        return obj.pretranslated

    def get_strings_with_warnings(self, obj):
        return obj.warnings

    def get_strings_with_errors(self, obj):
        return obj.errors

    def get_missing_strings(self, obj):
        return obj.missing

    def get_unreviewed_strings(self, obj):
        return obj.unreviewed

    def get_complete(self, obj):
        return obj.is_complete


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "slug",
            "name",
            "priority",
        )


class LocaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locale
        fields = [
            "code",
            "name",
            "direction",
            "population",
            "cldr_plurals",
            "plural_rule",
            "script",
            "google_translate_code",
            "ms_terminology_code",
            "ms_translator_code",
            "systran_translate_code",
            "team_description",
        ] + TRANSLATION_STATS_FIELDS


class ProjectSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "slug",
            "name",
            "priority",
            "deadline",
            "visibility",
            "contact",
            "info",
            "system_project",
            "disabled",
            "sync_disabled",
            "pretranslation_enabled",
        ] + TRANSLATION_STATS_FIELDS

    def get_contact(self, obj):
        if obj.contact:
            return obj.contact.username
        return None


class ProjectLocaleSerializer(TranslationStatsMixin, serializers.ModelSerializer):
    locale = serializers.SlugRelatedField(read_only=True, slug_field="code")

    class Meta:
        model = ProjectLocale
        fields = [
            "locale",
        ] + TRANSLATION_STATS_FIELDS


class NestedProjectSerializer(TranslationStatsMixin, ProjectSerializer):
    locales = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["tags", "locales"]

    def get_locales(self, obj):
        return [pl.locale.code for pl in getattr(obj, "fetched_project_locales", [])]


class NestedIndividualProjectSerializer(TranslationStatsMixin, ProjectSerializer):
    tags = TagSerializer(many=True, read_only=True)
    localizations = serializers.SerializerMethodField()

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["tags", "localizations"]

    def get_localizations(self, obj):
        request = self.context.get("request")
        if not request:
            return None

        project_locales = obj.project_locale.stats_data(project=obj)
        serialized = ProjectLocaleSerializer(project_locales, many=True).data

        return {
            item["locale"]: {k: v for k, v in item.items() if k != "locale"}
            for item in serialized
        }


class NestedLocaleSerializer(TranslationStatsMixin, LocaleSerializer):
    projects = serializers.SerializerMethodField()

    class Meta(LocaleSerializer.Meta):
        fields = LocaleSerializer.Meta.fields + ["projects"]

    def get_projects(self, obj):
        return [pl.project.slug for pl in getattr(obj, "fetched_project_locales", [])]


class NestedProjectLocaleSerializer(ProjectLocaleSerializer):
    locale = LocaleSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta(ProjectLocaleSerializer.Meta):
        fields = ProjectLocaleSerializer.Meta.fields + ["locale", "project"]


class TermSerializer(serializers.ModelSerializer):
    translation_text = serializers.SerializerMethodField()

    class Meta:
        model = Term
        fields = [
            "definition",
            "part_of_speech",
            "text",
            "translation_text",
            "usage",
            "notes",
        ]

    def get_translation_text(self, obj):
        request = self.context.get("request")
        locale = request.query_params.get("locale") if request else None

        if not locale:
            return None

        term = obj.translations.filter(locale__code=locale).first()
        return term.text if term else None


class TranslationMemorySerializer(serializers.ModelSerializer):
    locale = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = TranslationMemoryEntry
        fields = [
            "locale",
            "project",
            "source",
            "target",
        ]

    def get_locale(self, obj):
        return obj.locale.code

    def get_project(self, obj):
        if obj.project:
            return obj.project.slug
        return None
