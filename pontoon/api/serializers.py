from rest_framework import serializers

from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.terminology.models import Term


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
        ]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
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
        ]


class TermSerializer(serializers.ModelSerializer):
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
