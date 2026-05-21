"""
Tests for pontoon/projects/utils.py — CSV export and import helpers.

Key encoding convention (matches Entity.key ArrayField → CSV column round-trip):
  - plain_json / webext: array elements joined with "." (e.g. ["ns", "k"] → "ns.k")
  - all other formats: array elements joined with \x04 (e.g. ["ctx", "id"] → "ctx\x04id")

On import, get_translation_key() reverses these encodings to reconstruct the
list used for Entity.key exact-match lookups.
"""

import csv
import io
from unittest.mock import patch

import pytest

from pontoon.base.models import Resource, Translation
from pontoon.projects.utils import (
    generate_translation_stats_csv,
    get_translation_key,
    upload_translations,
)
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslationFactory,
    UserFactory,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def no_onboarding_email():
    """Suppress the post-save signal that renders an email template requiring
    collected static files — avoids 'Missing staticfiles manifest' errors when
    running tests without a prior collectstatic."""
    with patch("pontoon.base.signals.send_onboarding_email_1"):
        yield


# ─── Helpers ─────────────────────────────────────────────────────────────────


def make_csv_file(content: str) -> io.BytesIO:
    """Wrap a CSV string as a file-like object accepted by upload_translations."""
    return io.BytesIO(content.encode("utf-8"))


def build_csv(headers: list[str], rows: list[list]) -> str:
    """Build a quoted CSV string from headers and data rows."""
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_ALL)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def parse_csv_response(response) -> list[dict]:
    """Decode an HttpResponse body as CSV and return a list of row dicts."""
    return list(csv.DictReader(io.StringIO(response.content.decode("utf-8"))))


# ─── get_translation_key ─────────────────────────────────────────────────────


class TestGetTranslationKey:
    """
    get_translation_key converts a CSV "Translation Key" cell back to the
    Python list that matches Entity.key (an ArrayField) for DB lookup.
    """

    @pytest.mark.parametrize(
        "fmt, csv_key, expected",
        [
            # JSON formats: dot-separated path → list of path segments
            ("plain_json", "section.key", ["section", "key"]),
            ("plain_json", "top_level_key", ["top_level_key"]),
            ("webext", "hello_world", ["hello_world"]),
            # Non-JSON single-element keys: no separator present
            ("gettext", "Hello World", ["Hello World"]),
            ("android", "app_name", ["app_name"]),
            ("dtd", "foo.bar", ["foo.bar"]),
            ("properties", "key.name", ["key.name"]),
            ("fluent", "message-id", ["message-id"]),
            # ini: section prepended during sync (see migration 0091)
            ("ini", "Strings\x04Section\x04key", ["Strings", "Section", "key"]),
            # Gettext with msgctxt: stored as [msgid, msgctxt] after migration 0091
            ("gettext", "msgid\x04msgctxt", ["msgid", "msgctxt"]),
            # xcode / xliff: multi-part key with \x04 separator
            (
                "xcode",
                "Localizable.strings\x046SV-6v-92i.text",
                ["Localizable.strings", "6SV-6v-92i.text"],
            ),
            ("xliff", "file.xliff\x04unit-id", ["file.xliff", "unit-id"]),
        ],
    )
    def test_supported_formats(self, fmt, csv_key, expected):
        assert get_translation_key(key=csv_key, format=fmt) == expected

    def test_unsupported_format_returns_none(self):
        assert get_translation_key(key="anything", format="unknown_format") is None


# ─── generate_translation_stats_csv ──────────────────────────────────────────


class TestGenerateTranslationStatsCsv:
    """Tests for the CSV export function."""

    @pytest.fixture
    def locale(self):
        return LocaleFactory(name="Klingon", code="tlh")

    @pytest.fixture
    def project(self, locale):
        return ProjectFactory(slug="test-project", locales=[locale], repositories=[])

    @pytest.fixture
    def user(self):
        return UserFactory()

    # ── Response metadata ────────────────────────────────────────────────────

    @pytest.mark.django_db
    def test_content_type_and_filename(self, project, user):
        response = generate_translation_stats_csv(project=project, user=user)

        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert (
            response["Content-Disposition"]
            == 'attachment; filename="test-project_translations_stats.csv"'
        )

    @pytest.mark.django_db
    def test_headers_include_all_locale_names(self, project, locale, user):
        response = generate_translation_stats_csv(project=project, user=user)
        content = response.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)

        assert headers == [
            "Resource",
            "Translation Key",
            "Translation Source String",
            locale.name,
        ]

    # ── Entity key encoding ──────────────────────────────────────────────────

    @pytest.mark.django_db
    def test_gettext_key_written_as_plain_string(self, project, locale, user):
        """Single-element gettext keys are written as a plain string (no separator)."""
        resource = ResourceFactory(project=project, path="test.po", format="gettext")
        EntityFactory(resource=resource, string="Hello", key=["Hello"])

        rows = parse_csv_response(
            generate_translation_stats_csv(project=project, user=user)
        )

        assert rows[0]["Translation Key"] == "Hello"

    @pytest.mark.django_db
    def test_plain_json_key_is_dot_joined(self, project, locale, user):
        """plain_json keys (path segments) are joined with '.' in the CSV."""
        resource = ResourceFactory(
            project=project, path="strings.json", format="plain_json"
        )
        EntityFactory(resource=resource, string="Hello", key=["section", "greeting"])

        rows = parse_csv_response(
            generate_translation_stats_csv(project=project, user=user)
        )

        assert rows[0]["Translation Key"] == "section.greeting"

    @pytest.mark.django_db
    def test_xliff_multi_part_key_uses_separator(self, project, locale, user):
        """Multi-element xliff keys are joined with \\x04 to preserve all parts."""
        resource = ResourceFactory(
            project=project, path="test.xliff", format="xliff"
        )
        EntityFactory(
            resource=resource,
            string="Submit",
            key=["Localizable.strings", "btn_submit"],
        )

        rows = parse_csv_response(
            generate_translation_stats_csv(project=project, user=user)
        )

        assert rows[0]["Translation Key"] == "Localizable.strings\x04btn_submit"

    # ── Translation content ──────────────────────────────────────────────────

    @pytest.mark.django_db
    def test_approved_translation_in_locale_column(self, project, locale, user):
        resource = ResourceFactory(project=project, path="test.po", format="gettext")
        entity = EntityFactory(resource=resource, string="Hello", key=["Hello"])
        TranslationFactory(
            entity=entity, locale=locale, string="Hola", approved=True
        )

        rows = parse_csv_response(
            generate_translation_stats_csv(project=project, user=user)
        )

        assert rows[0][locale.name] == "Hola"

    @pytest.mark.django_db
    def test_unapproved_translation_not_exported(self, project, locale, user):
        """Only approved translations appear in locale columns; others are blank."""
        resource = ResourceFactory(project=project, path="test.po", format="gettext")
        entity = EntityFactory(resource=resource, string="Hello", key=["Hello"])
        TranslationFactory(
            entity=entity, locale=locale, string="Hola", approved=False
        )

        rows = parse_csv_response(
            generate_translation_stats_csv(project=project, user=user)
        )

        assert rows[0][locale.name] == ""

    @pytest.mark.django_db
    def test_entity_with_no_translation_has_empty_locale_cell(
        self, project, locale, user
    ):
        resource = ResourceFactory(project=project, path="test.po", format="gettext")
        EntityFactory(resource=resource, string="Hello", key=["Hello"])

        rows = parse_csv_response(
            generate_translation_stats_csv(project=project, user=user)
        )

        assert rows[0][locale.name] == ""

    @pytest.mark.django_db
    def test_obsolete_entities_excluded(self, project, locale, user):
        resource = ResourceFactory(project=project, path="test.po", format="gettext")
        EntityFactory(resource=resource, string="Active", key=["Active"])
        EntityFactory(resource=resource, string="Old", key=["Old"], obsolete=True)

        rows = parse_csv_response(
            generate_translation_stats_csv(project=project, user=user)
        )

        assert len(rows) == 1
        assert rows[0]["Translation Source String"] == "Active"

    @pytest.mark.django_db
    def test_multiple_locales(self, user):
        # Use codes that don't clash with the class-level locale fixture ("tlh").
        locale1 = LocaleFactory(name="Geonosian", code="geo")
        locale2 = LocaleFactory(name="Dothraki", code="dth")
        project = ProjectFactory(
            slug="multi-locale-project",
            locales=[locale1, locale2],
            repositories=[],
        )
        resource = ResourceFactory(project=project, path="test.po", format="gettext")
        entity = EntityFactory(resource=resource, string="Hello", key=["Hello"])
        TranslationFactory(
            entity=entity, locale=locale1, string="Hola", approved=True
        )
        TranslationFactory(
            entity=entity, locale=locale2, string="Bona", approved=True
        )

        rows = parse_csv_response(
            generate_translation_stats_csv(project=project, user=user)
        )

        assert rows[0]["Geonosian"] == "Hola"
        assert rows[0]["Dothraki"] == "Bona"


# ─── upload_translations ─────────────────────────────────────────────────────


class TestUploadTranslations:
    """Tests for the CSV import function."""

    @pytest.fixture
    def locale(self):
        return LocaleFactory(name="Klingon", code="tlh")

    @pytest.fixture
    def project(self, locale):
        return ProjectFactory(slug="test-project", locales=[locale], repositories=[])

    @pytest.fixture
    def resource(self, project):
        return ResourceFactory(project=project, path="test.po", format="gettext")

    @pytest.fixture
    def entity(self, resource):
        return EntityFactory(resource=resource, string="Hello", key=["Hello"])

    @pytest.fixture
    def user(self):
        return UserFactory()

    @pytest.fixture
    def translator(self, project, locale):
        """A user with translator rights for this project/locale."""
        user = UserFactory()
        project_locale = project.project_locale.get(locale=locale)
        user.groups.add(project_locale.translators_group)
        return user

    def _csv(self, locale_name, rows, *, extra_headers=None):
        headers = ["Resource", "Translation Key", "Translation Source String", locale_name]
        if extra_headers:
            headers += extra_headers
        return build_csv(headers, rows)

    # ── Validation errors ────────────────────────────────────────────────────

    @pytest.mark.django_db
    def test_too_few_headers_returns_400(self, project, user):
        csv_file = make_csv_file(
            build_csv(["Resource", "Translation Key", "Source"], [])
        )
        response = upload_translations(csv_file=csv_file, project=project, user=user)

        assert response.status_code == 400
        assert "Wrong CSV headers" in response.content.decode()

    @pytest.mark.django_db
    def test_unknown_locale_returns_400(self, project, user):
        csv_file = make_csv_file(
            build_csv(
                ["Resource", "Translation Key", "Source", "Martian"],
                [["test.po", "Hello", "Hello", "Boo"]],
            )
        )
        response = upload_translations(csv_file=csv_file, project=project, user=user)

        assert response.status_code == 400
        assert "Not recognizable locale names" in response.content.decode()

    @pytest.mark.django_db
    def test_unknown_resource_path_returns_400(self, project, locale, entity, user):
        csv_file = make_csv_file(
            self._csv(
                locale.name,
                [["nonexistent.po", "Hello", "Hello", "Hola"]],
            )
        )
        response = upload_translations(csv_file=csv_file, project=project, user=user)

        assert response.status_code == 400
        assert "Resource not found" in response.content.decode()

    @pytest.mark.django_db
    def test_unknown_translation_key_returns_400(
        self, project, locale, resource, entity, user
    ):
        csv_file = make_csv_file(
            self._csv(
                locale.name,
                [["test.po", "NonExistentKey", "Hello", "Hola"]],
            )
        )
        response = upload_translations(csv_file=csv_file, project=project, user=user)

        assert response.status_code == 400
        assert "does not exist" in response.content.decode()

    # ── Skipped rows ─────────────────────────────────────────────────────────

    @pytest.mark.django_db
    def test_empty_locale_cell_is_skipped(
        self, project, locale, resource, entity, user
    ):
        csv_file = make_csv_file(
            self._csv(locale.name, [["test.po", "Hello", "Hello", ""]])
        )
        upload_translations(csv_file=csv_file, project=project, user=user)

        assert not Translation.objects.filter(entity=entity, locale=locale).exists()

    @pytest.mark.parametrize("mark", ["MISSING", "PRETRANSLATED", "REJECTED", "FUZZY", "UNREVIEWED"])
    @pytest.mark.django_db
    def test_untranslated_marks_are_skipped(
        self, project, locale, resource, entity, user, mark
    ):
        csv_file = make_csv_file(
            self._csv(locale.name, [["test.po", "Hello", "Hello", mark]])
        )
        upload_translations(csv_file=csv_file, project=project, user=user)

        assert not Translation.objects.filter(entity=entity, locale=locale).exists()

    @pytest.mark.django_db
    def test_duplicate_string_is_not_created_twice(
        self, project, locale, resource, entity, user
    ):
        TranslationFactory(entity=entity, locale=locale, string="Hola", approved=True)

        csv_file = make_csv_file(
            self._csv(locale.name, [["test.po", "Hello", "Hello", "Hola"]])
        )
        upload_translations(csv_file=csv_file, project=project, user=user)

        assert Translation.objects.filter(entity=entity, locale=locale).count() == 1

    # ── Translation creation ─────────────────────────────────────────────────

    @pytest.mark.django_db
    def test_creates_unapproved_translation_for_non_translator(
        self, project, locale, resource, entity, user
    ):
        """Users without translator rights create unapproved, inactive translations."""
        csv_file = make_csv_file(
            self._csv(locale.name, [["test.po", "Hello", "Hello", "Hola"]])
        )
        result = upload_translations(csv_file=csv_file, project=project, user=user)

        assert result is None  # None means success; view handles redirect
        tr = Translation.objects.get(entity=entity, locale=locale)
        assert tr.string == "Hola"
        assert tr.approved is False
        assert tr.active is False

    @pytest.mark.django_db
    def test_creates_approved_translation_for_translator(
        self, project, locale, resource, entity, translator
    ):
        """Translators create approved, active translations."""
        csv_file = make_csv_file(
            self._csv(locale.name, [["test.po", "Hello", "Hello", "Hola"]])
        )
        result = upload_translations(
            csv_file=csv_file, project=project, user=translator
        )

        assert result is None
        tr = Translation.objects.get(entity=entity, locale=locale)
        assert tr.string == "Hola"
        assert tr.approved is True
        assert tr.active is True
        assert tr.approved_user == translator

    @pytest.mark.django_db
    def test_translator_import_deactivates_previous_active_translation(
        self, project, locale, resource, entity, translator
    ):
        """When a translator imports a new string the existing active translation is
        deactivated atomically before the new one is saved."""
        old = TranslationFactory(
            entity=entity, locale=locale, string="Old Translation",
            approved=True, active=True,
        )

        csv_file = make_csv_file(
            self._csv(locale.name, [["test.po", "Hello", "Hello", "New Translation"]])
        )
        upload_translations(csv_file=csv_file, project=project, user=translator)

        old.refresh_from_db()
        assert old.active is False

        new = Translation.objects.get(entity=entity, locale=locale, string="New Translation")
        assert new.approved is True
        assert new.active is True

    # ── Format round-trips ───────────────────────────────────────────────────

    @pytest.mark.django_db
    def test_plain_json_dot_key_lookup(self, project, locale, user):
        """plain_json keys exported as 'ns.key' are correctly resolved on import."""
        resource = ResourceFactory(
            project=project, path="strings.json", format="plain_json"
        )
        entity = EntityFactory(
            resource=resource, string="Hello", key=["ns", "greeting"]
        )

        csv_file = make_csv_file(
            build_csv(
                ["Resource", "Translation Key", "Translation Source String", locale.name],
                [["strings.json", "ns.greeting", "Hello", "Hola"]],
            )
        )
        result = upload_translations(csv_file=csv_file, project=project, user=user)

        assert result is None
        assert Translation.objects.filter(entity=entity, locale=locale).exists()

    @pytest.mark.django_db
    def test_xliff_multi_part_key_lookup(self, project, locale, user):
        """xliff keys exported with \\x04 separator are correctly resolved on import."""
        resource = ResourceFactory(
            project=project, path="test.xliff", format="xliff"
        )
        entity = EntityFactory(
            resource=resource, string="Submit", key=["Localizable.strings", "btn_submit"]
        )

        csv_file = make_csv_file(
            build_csv(
                ["Resource", "Translation Key", "Translation Source String", locale.name],
                [["test.xliff", "Localizable.strings\x04btn_submit", "Submit", "Abschicken"]],
            )
        )
        result = upload_translations(csv_file=csv_file, project=project, user=user)

        assert result is None
        assert Translation.objects.filter(entity=entity, locale=locale).exists()
