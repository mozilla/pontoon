from rest_framework import serializers

from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    TranslationMemoryEntry,
)
from pontoon.base.models.entity import Entity
from pontoon.base.models.resource import Resource
from pontoon.base.models.translation import Translation
from pontoon.base.simple_preview import get_simple_preview
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


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Serializer that takes an additional `fields` argument
    to control which fields should be returned.
    """

    def __init__(self, *args, **kwargs):
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request:
            fields_param = request.query_params.get("fields")
            if fields_param:
                allowed = set(fields_param.split(","))
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "slug",
            "name",
            "priority",
        )


class LocaleSerializer(DynamicFieldsModelSerializer):
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


class ProjectSerializer(DynamicFieldsModelSerializer):
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


class CompactProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "slug",
            "name",
        ]


class CompactLocaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locale
        fields = [
            "code",
            "name",
        ]


class ProjectLocaleSerializer(TranslationStatsMixin, DynamicFieldsModelSerializer):
    locale = CompactLocaleSerializer(read_only=True)
    project = CompactProjectSerializer(read_only=True)

    class Meta:
        model = ProjectLocale
        fields = [
            "locale",
            "project",
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
    locales = serializers.SerializerMethodField()
    localizations = serializers.SerializerMethodField()

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["tags", "locales", "localizations"]

    def get_locales(self, obj):
        return [pl.locale.code for pl in getattr(obj, "fetched_project_locales", [])]

    def get_localizations(self, obj):
        project_locales = obj.project_locale.stats_data(project=obj)
        serialized = ProjectLocaleSerializer(project_locales, many=True).data
        return [
            {k: v for k, v in item.items() if k != "project"} for item in serialized
        ]


class NestedLocaleSerializer(TranslationStatsMixin, LocaleSerializer):
    projects = serializers.SerializerMethodField()

    class Meta(LocaleSerializer.Meta):
        fields = LocaleSerializer.Meta.fields + ["projects"]

    def get_projects(self, obj):
        return [pl.project.slug for pl in getattr(obj, "fetched_project_locales", [])]


class NestedIndividualLocaleSerializer(TranslationStatsMixin, LocaleSerializer):
    projects = serializers.SerializerMethodField()
    localizations = serializers.SerializerMethodField()

    class Meta(LocaleSerializer.Meta):
        fields = LocaleSerializer.Meta.fields + ["projects", "localizations"]

    def get_projects(self, obj):
        return [pl.project.slug for pl in getattr(obj, "fetched_project_locales", [])]

    def get_localizations(self, obj):
        project_locales = obj.project_locale.stats_data(locale=obj)
        serialized = ProjectLocaleSerializer(project_locales, many=True).data
        return [{k: v for k, v in item.items() if k != "locale"} for item in serialized]


class NestedProjectLocaleSerializer(ProjectLocaleSerializer):
    locale = LocaleSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta(ProjectLocaleSerializer.Meta):
        fields = ProjectLocaleSerializer.Meta.fields + ["locale", "project"]


class TermSerializer(DynamicFieldsModelSerializer):
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
        if hasattr(obj, "filtered_translations") and (ft := obj.filtered_translations):
            return ft[0].text

        return None


class TranslationMemorySerializer(DynamicFieldsModelSerializer):
    locale = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = TranslationMemoryEntry
        fields = [
            "locale",
            "project",
            "entity",
            "source",
            "target",
        ]

    def get_locale(self, obj):
        return obj.locale.code

    def get_project(self, obj):
        if obj.project:
            return obj.project.slug
        return None


class TranslationSerializer(serializers.ModelSerializer):
    locale = serializers.SerializerMethodField()
    string = serializers.SerializerMethodField()

    class Meta:
        model = Translation
        fields = [
            "locale",
            "string",
        ]

    def get_locale(self, obj):
        if not obj.locale:
            return None

        return {
            "code": obj.locale.code,
            "name": obj.locale.name,
        }

    def get_string(self, obj):
        return get_simple_preview(obj.entity.resource.format, obj.string)


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            "path",
        ]


class EntitySerializer(DynamicFieldsModelSerializer):
    entity = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    resource = ResourceSerializer(read_only=True)

    class Meta:
        model = Entity
        fields = [
            "id",
            "string",
            "key",
            "project",
            "resource",
        ]

    def get_string(self, obj):
        return get_simple_preview(obj.resource.format, obj.string)

    def get_project(self, obj):
        if not obj.resource.project:
            return None

        return {
            "slug": obj.resource.project.slug,
            "name": obj.resource.project.name,
        }


class NestedEntitySerializer(EntitySerializer):
    translations = serializers.SerializerMethodField()

    class Meta(EntitySerializer.Meta):
        fields = EntitySerializer.Meta.fields + ["translations"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "context" in kwargs:
            if "request" in kwargs["context"]:
                include_translations = kwargs["context"]["request"].query_params.get(
                    "include_translations"
                )

                if include_translations is None:
                    self.fields.pop("translations", None)

    def get_translations(self, obj):
        return TranslationSerializer(
            obj.filtered_translations, many=True, context=self.context
        ).data


class EntitySearchSerializer(EntitySerializer):
    translation = serializers.SerializerMethodField()

    class Meta(EntitySerializer.Meta):
        fields = EntitySerializer.Meta.fields + ["translation"]

    def get_translation(self, obj):
        request = self.context.get("request")

        if not request:
            return None

        translation = obj.active_translations[0] if obj.active_translations else None

        return TranslationSerializer(translation, context=self.context).data
