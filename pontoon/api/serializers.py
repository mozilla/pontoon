from rest_framework import serializers

from django.shortcuts import get_object_or_404

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
            "approved_strings",
            "cldr_plurals",
            "complete",
            "direction",
            "google_translate_code",
            "missing_strings",
            "ms_terminology_code",
            "ms_translator_code",
            "name",
            "plural_rule",
            "population",
            "pretranslated_strings",
            "script",
            "strings_with_errors",
            "strings_with_warnings",
            "systran_translate_code",
            "team_description",
            "total_strings",
            "unreviewed_strings",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "approved_strings",
            "complete",
            "contact",
            "deadline",
            "disabled",
            "info",
            "missing_strings",
            "name",
            "pretranslated_strings",
            "pretranslation_enabled",
            "priority",
            "slug",
            "strings_with_errors",
            "strings_with_warnings",
            "sync_disabled",
            "system_project",
            "total_strings",
            "unreviewed_strings",
            "visibility",
        ]

    def get_contact(self, obj):
        if obj.contact:
            return obj.contact.username
        return None


class ProjectLocaleSerializer(serializers.ModelSerializer):
    locale = serializers.SerializerMethodField()
    approved_strings = serializers.SerializerMethodField()
    missing_strings = serializers.SerializerMethodField()
    pretranslated_strings = serializers.SerializerMethodField()
    strings_with_errors = serializers.SerializerMethodField()
    strings_with_warnings = serializers.SerializerMethodField()
    total_strings = serializers.SerializerMethodField()
    unreviewed_strings = serializers.SerializerMethodField()

    class Meta:
        model = ProjectLocale
        fields = [
            "locale",
            "total_strings",
            "approved_strings",
            "pretranslated_strings",
            "strings_with_errors",
            "strings_with_warnings",
            "missing_strings",
            "unreviewed_strings",
        ]

    def get_locale(self, obj):
        return obj.locale.code

    def get_approved_strings(self, obj):
        return obj.approved

    def get_missing_strings(self, obj):
        return obj.missing

    def get_pretranslated_strings(self, obj):
        return obj.pretranslated

    def get_strings_with_errors(self, obj):
        return obj.errors

    def get_strings_with_warnings(self, obj):
        return obj.warnings

    def get_total_strings(self, obj):
        return obj.total

    def get_unreviewed_strings(self, obj):
        return obj.unreviewed



class NestedProjectSerializer(ProjectSerializer):
    locales = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    approved_strings = serializers.SerializerMethodField()
    complete = serializers.SerializerMethodField()
    missing_strings = serializers.SerializerMethodField()
    pretranslated_strings = serializers.SerializerMethodField()
    strings_with_errors = serializers.SerializerMethodField()
    strings_with_warnings = serializers.SerializerMethodField()
    total_strings = serializers.SerializerMethodField()
    unreviewed_strings = serializers.SerializerMethodField()

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["tags", "locales"]

    def get_locales(self, obj):
        return [pl.locale.code for pl in obj.project_locale.visible()]

    def get_approved_strings(self, obj):
        return obj.approved

    def get_complete(self, obj):
        return obj.is_complete

    def get_missing_strings(self, obj):
        return obj.missing

    def get_pretranslated_strings(self, obj):
        return obj.pretranslated

    def get_strings_with_errors(self, obj):
        return obj.errors

    def get_strings_with_warnings(self, obj):
        return obj.warnings

    def get_total_strings(self, obj):
        return obj.total

    def get_unreviewed_strings(self, obj):
        return obj.unreviewed


class NestedIndividualProjectSerializer(ProjectSerializer):
    tags = TagSerializer(many=True, read_only=True)
    project_locale = serializers.SerializerMethodField()

    approved_strings = serializers.SerializerMethodField()
    complete = serializers.SerializerMethodField()
    missing_strings = serializers.SerializerMethodField()
    pretranslated_strings = serializers.SerializerMethodField()
    strings_with_errors = serializers.SerializerMethodField()
    strings_with_warnings = serializers.SerializerMethodField()
    total_strings = serializers.SerializerMethodField()
    unreviewed_strings = serializers.SerializerMethodField()

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["tags", "project_locale"]

    def get_approved_strings(self, obj):
        return obj.approved

    def get_complete(self, obj):
        return obj.is_complete

    def get_missing_strings(self, obj):
        return obj.missing

    def get_pretranslated_strings(self, obj):
        return obj.pretranslated

    def get_strings_with_errors(self, obj):
        return obj.errors

    def get_strings_with_warnings(self, obj):
        return obj.warnings

    def get_total_strings(self, obj):
        return obj.total

    def get_unreviewed_strings(self, obj):
        return obj.unreviewed

    def get_project_locale(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        slug = self.context['view'].kwargs.get('slug')
        project = get_object_or_404(
            Project,
            slug=slug,
        )

        project_locales = obj.project_locale.stats_data(project=project)
        return ProjectLocaleSerializer(project_locales, many=True).data


class NestedLocaleSerializer(LocaleSerializer):
    projects = serializers.SerializerMethodField()

    approved_strings = serializers.SerializerMethodField()
    complete = serializers.SerializerMethodField()
    missing_strings = serializers.SerializerMethodField()
    pretranslated_strings = serializers.SerializerMethodField()
    strings_with_errors = serializers.SerializerMethodField()
    strings_with_warnings = serializers.SerializerMethodField()
    total_strings = serializers.SerializerMethodField()
    unreviewed_strings = serializers.SerializerMethodField()

    class Meta(LocaleSerializer.Meta):
        fields = LocaleSerializer.Meta.fields + ["projects"]

    def get_projects(self, obj):
        return [pl.project.slug for pl in obj.project_locale.visible()]

    def get_approved_strings(self, obj):
        return obj.approved

    def get_complete(self, obj):
        return obj.is_complete

    def get_missing_strings(self, obj):
        return obj.missing

    def get_pretranslated_strings(self, obj):
        return obj.pretranslated

    def get_strings_with_errors(self, obj):
        return obj.errors

    def get_strings_with_warnings(self, obj):
        return obj.warnings

    def get_total_strings(self, obj):
        return obj.total

    def get_unreviewed_strings(self, obj):
        return obj.unreviewed


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

        for translated_term in obj.translations.all():
            if translated_term.locale.code == locale:
                return translated_term.text


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
