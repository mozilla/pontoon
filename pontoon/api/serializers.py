from rest_framework import serializers

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

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagModel
        fields = (
            "slug",
            "name",
            "priority",
        )

class ProjectLocaleSerializer(serializers.ModelSerializer):
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

class LocaleSerializer(serializers.ModelSerializer):
    project_locale = ProjectLocaleSerializer(many=True, read_only=True)

    class Meta:
        model = LocaleModel
        fields = [
            "code",
            "approved_strings",
            "cldr_plurals",
            "complete",
            "direction",
            "google_translate_code",
            "missing_strings",
            "ms_translator_code",
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
            "project_locale"
        ]


class ProjectSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProjectModel
        fields = [
            "approved_strings",
            "complete",
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
            "tag"
        ]

class TermTranslationSerializer(serializers.ModelSerializer):
    # locale = LocaleSerializer(read_only=True)

    class Meta:
        model = TermTranslationModel
        fields = ["text", "locale"]

class TermSerializer(serializers.ModelSerializer):
    translations = TermTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = TermModel
        fields = [
            "definition",
            "part_of_speech",
            "text",
            "usage",
            "notes",
            "translations"
        ]

class TranslationMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationMemoryEntryModel
        fields = [
            "source",
            "target",
        ]