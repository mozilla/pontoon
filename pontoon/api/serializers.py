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
    "completed_strings",
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
    completed_strings = serializers.SerializerMethodField()
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

    def get_completed_strings(self, obj):
        return obj.completed

    def get_complete(self, obj):
        return obj.is_complete


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Serializer that takes an additional `fields` argument
    to control which fields should be returned.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    script_name = serializers.SerializerMethodField()

    def get_script_name(self, obj) -> str:
        """English name of the script, e.g. "Latin" for "Latn". Empty if unset."""
        return obj.get_script_display()

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
            "script_name",
            "google_translate_code",
            "ms_terminology_code",
            "ms_translator_code",
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
        if obj.do_not_translate:
            return obj.text

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


class UserActionUserSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    name = serializers.CharField()
    system_user = serializers.BooleanField()


class UserActionLocaleSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()


class UserActionEntitySerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    key = serializers.ListField(child=serializers.CharField())


class UserActionResourceSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    path = serializers.CharField()
    format = serializers.ChoiceField(choices=Resource.Format.values, allow_blank=True)


class UserActionTranslationSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    status = serializers.CharField()
    string = serializers.CharField()
    value = serializers.JSONField()
    properties = serializers.JSONField(required=False)
    errors = serializers.ListField(child=serializers.CharField(), required=False)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)


class UserActionSerializer(serializers.Serializer):
    type = serializers.CharField()
    is_implicit_action = serializers.BooleanField()
    date = serializers.DateTimeField()
    user = UserActionUserSerializer()
    locale = UserActionLocaleSerializer()
    entity = UserActionEntitySerializer()
    resource = UserActionResourceSerializer()
    translation = UserActionTranslationSerializer(required=False)


class UserActionsProjectSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    slug = serializers.CharField()
    name = serializers.CharField()


class UserActionsResponseSerializer(serializers.Serializer):
    """Response returned by the user-actions endpoint."""

    actions = UserActionSerializer(many=True)
    project = UserActionsProjectSerializer()


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["path", "format"]


class EntitySerializer(DynamicFieldsModelSerializer):
    string = serializers.SerializerMethodField()
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
                include_translations = (
                    kwargs["context"]["request"]
                    .query_params.get("include_translations", "false")
                    .lower()
                )

                if include_translations != "true":
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


class PretranslationResponseSerializer(serializers.Serializer):
    """Result of pretranslating a source string."""

    text = serializers.CharField(help_text="Pretranslation of the source string.")
    author = serializers.ChoiceField(
        choices=["gt", "tm"],
        help_text="Service that provided the pretranslation: Google Translate or TM.",
    )


# A serializer would document `uploadfile` as a plain string unless
# `COMPONENT_SPLIT_REQUEST` is enabled for the whole API, so the request is described
# with a raw OpenAPI schema here.
UPLOAD_REQUEST_SCHEMA = {
    "type": "object",
    "description": (
        "Translation file to import, with the project, locale and resource it targets."
    ),
    "properties": {
        "project": {"type": "string", "description": "Project slug."},
        "locale": {"type": "string", "description": "Locale code."},
        "resource": {
            "type": "string",
            "description": "Resource path within the project.",
        },
        "uploadfile": {
            "type": "string",
            "format": "binary",
            "description": (
                "Translation file, in the same format as the target resource."
            ),
        },
    },
    "required": ["project", "locale", "resource", "uploadfile"],
}


# For large files, only report the first keys that could not be imported, alongside
# their total number.
UPLOAD_KEYS_ERROR_LIMIT = 100


def undefined_keys_field() -> serializers.ListField:
    """Upload response field listing the keys that match no entity in Pontoon."""
    return serializers.ListField(
        child=serializers.ListField(child=serializers.CharField()),
        help_text=f"Keys of translations with no matching entity in Pontoon, ignored. "
        f"Truncated to the first {UPLOAD_KEYS_ERROR_LIMIT} keys.",
    )


def undefined_keys_count_field() -> serializers.IntegerField:
    """Upload response field counting the keys that match no entity in Pontoon."""
    return serializers.IntegerField(
        help_text="Total number of keys with no matching entity in Pontoon, "
        "before truncation."
    )


class BadgeUpdateSerializer(serializers.Serializer):
    """A badge level the user reached through the upload."""

    name = serializers.CharField(help_text="Name of the badge.")
    level = serializers.IntegerField(help_text="Level reached.")


def badge_updates_field() -> BadgeUpdateSerializer:
    """Upload response field listing the badge levels the user reached."""
    return BadgeUpdateSerializer(
        many=True,
        help_text="Badges whose level the upload raised, with the new level. "
        "The user is also notified of each.",
    )


class UploadTranslationsResponseSerializer(serializers.Serializer):
    """Result of a translation file upload."""

    updated = serializers.IntegerField(
        help_text="Number of translations added or replaced by the upload."
    )
    unchanged = serializers.IntegerField(
        help_text="Number of translations identical to the current ones, ignored."
    )
    undefined_keys = undefined_keys_field()
    undefined_keys_count = undefined_keys_count_field()
    badge_updates = badge_updates_field()


class FailedCheckSerializer(serializers.Serializer):
    """An uploaded translation left out because it fails quality checks."""

    key = serializers.ListField(
        child=serializers.CharField(),
        help_text="Key of the string, in the same format as the `key` field of "
        "entities.",
    )
    errors = serializers.ListField(
        child=serializers.CharField(),
        help_text="Errors reported by the quality checks.",
    )
    warnings = serializers.ListField(
        child=serializers.CharField(),
        help_text="Warnings reported by the quality checks.",
    )


class UploadPretranslationsResponseSerializer(serializers.Serializer):
    """Result of a pretranslation file upload."""

    created = serializers.IntegerField(
        help_text="Number of pretranslations added for strings with no pretranslation "
        "or fuzzy translation."
    )
    replaced = serializers.IntegerField(
        help_text="Number of pretranslations replacing a previous, different "
        "pretranslation or fuzzy translation."
    )
    converted = serializers.IntegerField(
        help_text="Number of existing translations made the active pretranslation, "
        "because they match the uploaded translation."
    )
    unchanged = serializers.IntegerField(
        help_text="Number of translations identical to the current pretranslation, "
        "ignored."
    )
    skipped = serializers.IntegerField(
        help_text="Number of strings left untouched, because they already have an "
        "approved translation, or are marked as fuzzy in the uploaded file."
    )
    failed_checks = FailedCheckSerializer(
        many=True,
        help_text="Strings left untouched, because the uploaded translation fails "
        f"quality checks. Truncated to the first {UPLOAD_KEYS_ERROR_LIMIT} keys.",
    )
    failed_checks_count = serializers.IntegerField(
        help_text="Total number of strings left untouched because of failing checks, "
        "before truncation."
    )
    undefined_keys = undefined_keys_field()
    undefined_keys_count = undefined_keys_count_field()
    badge_updates = badge_updates_field()


class UploadSuggestionsResponseSerializer(serializers.Serializer):
    """Result of a suggestion file upload."""

    created = serializers.IntegerField(
        help_text="Number of suggestions added by the upload."
    )
    restored = serializers.IntegerField(
        help_text="Number of rejected translations matching the upload that were "
        "un-rejected, becoming pending suggestions again."
    )
    unchanged = serializers.IntegerField(
        help_text="Number of uploaded translations that the string already has as an "
        "unrejected translation, in any review state, ignored."
    )
    failed_checks = FailedCheckSerializer(
        many=True,
        help_text="Strings left untouched, because the uploaded translation has "
        f"errors. Truncated to the first {UPLOAD_KEYS_ERROR_LIMIT} keys.",
    )
    failed_checks_count = serializers.IntegerField(
        help_text="Total number of strings left untouched because of errors, "
        "before truncation."
    )
    undefined_keys = undefined_keys_field()
    undefined_keys_count = undefined_keys_count_field()
    badge_updates = badge_updates_field()
