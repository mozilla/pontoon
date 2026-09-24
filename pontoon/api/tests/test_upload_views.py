from datetime import timedelta

import pytest

from notifications.models import Notification
from rest_framework.test import APIClient
from rest_framework.throttling import SimpleRateThrottle

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.utils.timezone import now

from pontoon.actionlog.models import ActionLog
from pontoon.api.models import PersonalAccessToken
from pontoon.api.serializers import UPLOAD_KEYS_ERROR_LIMIT
from pontoon.base import badge_utils
from pontoon.base.models import ChangedEntityLocale, Project, Translation
from pontoon.sync import upload as sync_upload
from pontoon.sync.upload import UploadConflictError
from pontoon.test.factories import EntityFactory, TranslationFactory


TRANSLATIONS = "/api/v2/upload/translations/"
PRETRANSLATIONS = "/api/v2/upload/pretranslations/"
SUGGESTIONS = "/api/v2/upload/suggestions/"
ENDPOINTS = [TRANSLATIONS, PRETRANSLATIONS, SUGGESTIONS]

# The importer each endpoint calls, as named in `pontoon.sync.upload`.
IMPORTERS = {
    TRANSLATIONS: "import_uploaded_file",
    PRETRANSLATIONS: "import_uploaded_pretranslations",
    SUGGESTIONS: "import_uploaded_suggestions",
}

PO_CONTENTS = 'msgid "test_key"\nmsgstr "new translation"'


def _pat_client(user):
    token = PersonalAccessToken.objects.create(
        user=user,
        name="Upload Token",
        token_hash="placeholder",
        expires_at=now() + timedelta(days=1),
    )
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.id}_{token_unhashed}")
    return client


def _po_file(contents=PO_CONTENTS, name="resource_a.po"):
    return SimpleUploadedFile(name, contents.encode("utf-8"))


def _post(client, url, **data):
    return client.post(url, data, format="multipart")


def _approved_translation(
    project_locale, resource, key, string="other translation", obsolete=False
):
    """An entity with an approved translation, in the resource of an upload."""
    return TranslationFactory.create(
        entity=EntityFactory.create(
            resource=resource, string=key, key=[key], obsolete=obsolete
        ),
        locale=project_locale.locale,
        string=string,
        value=[string],
        approved=True,
        active=True,
    )


def _upload(client, url, project_locale, resource_path, contents=PO_CONTENTS):
    return _post(
        client,
        url,
        project=project_locale.project.slug,
        locale=project_locale.locale.code,
        resource=resource_path,
        uploadfile=_po_file(contents),
    )


@pytest.fixture
def upload_translator(member, project_locale_a):
    project_locale_a.locale.translators_group.user_set.add(member.user)
    return member


@pytest.fixture
def pretranslator(upload_translator):
    """A translator who may also upload pretranslations, so any endpoint accepts them."""
    upload_translator.user.groups.add(Group.objects.get(name="pretranslators"))
    return upload_translator


@pytest.fixture
def upload_po_translation(translation_a):
    translation_a.entity.key = ["test_key"]
    translation_a.entity.save()
    return translation_a


@pytest.fixture
def resource_path(upload_po_translation):
    return upload_po_translation.entity.resource.path


@pytest.fixture
def untranslated_entity(upload_po_translation):
    """An entity without translations, in the same resource as `upload_po_translation`."""
    return EntityFactory.create(
        resource=upload_po_translation.entity.resource,
        string="Other entity",
        key=["other_key"],
    )


# Authentication and permissions, shared by all upload endpoints


@pytest.mark.django_db
@pytest.mark.parametrize("url", ENDPOINTS)
def test_upload_requires_authentication(url, project_locale_a, resource_path):
    response = _upload(APIClient(), url, project_locale_a, resource_path)

    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize("url", ENDPOINTS)
def test_upload_session_auth(url, pretranslator, project_locale_a, resource_path):
    """The translate app uploads with its session, without a token."""
    client = APIClient()
    # force_authenticate() would bypass authentication_classes.
    client.force_login(pretranslator.user)

    response = _upload(client, url, project_locale_a, resource_path)

    assert response.status_code == 200
    assert Translation.objects.filter(string="new translation").exists()


@pytest.mark.django_db
@pytest.mark.parametrize("url", ENDPOINTS)
def test_upload_session_auth_requires_csrf_token(
    url, pretranslator, project_locale_a, resource_path
):
    """Session requests are subject to CSRF checks, unlike token requests."""
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(pretranslator.user)

    response = _upload(client, url, project_locale_a, resource_path)

    assert response.status_code == 403
    assert "CSRF" in response.json()["detail"]
    assert not Translation.objects.filter(string="new translation").exists()


@pytest.mark.django_db
@pytest.mark.parametrize("url", ENDPOINTS)
def test_upload_requires_translate_permission(
    url, member, project_locale_a, resource_path
):
    """Membership of the pretranslators group alone is not enough either."""
    member.user.groups.add(Group.objects.get(name="pretranslators"))

    response = _upload(_pat_client(member.user), url, project_locale_a, resource_path)

    assert response.status_code == 403
    assert not Translation.objects.filter(string="new translation").exists()


@pytest.mark.django_db
@pytest.mark.parametrize("url", ENDPOINTS)
def test_upload_readonly_project_locale(
    url, pretranslator, project_locale_a, resource_path
):
    project_locale_a.readonly = True
    project_locale_a.save()

    response = _upload(
        _pat_client(pretranslator.user), url, project_locale_a, resource_path
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_pretranslations_requires_pretranslators_group(
    upload_translator, project_locale_a, resource_path
):
    """Translator rights alone are not enough."""
    response = _upload(
        _pat_client(upload_translator.user),
        PRETRANSLATIONS,
        project_locale_a,
        resource_path,
    )

    assert response.status_code == 403
    assert not Translation.objects.filter(pretranslated=True).exists()


@pytest.mark.django_db
def test_upload_admin_can_upload(member, project_locale_a, resource_path):
    member.user.is_superuser = True
    member.user.save()

    assert not project_locale_a.locale.translators_group.user_set.filter(
        pk=member.user.pk
    ).exists()

    response = _upload(
        _pat_client(member.user), TRANSLATIONS, project_locale_a, resource_path
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 1


# Request validation and target lookup, shared by all upload endpoints


@pytest.mark.django_db
@pytest.mark.parametrize("missing", ["project", "locale", "resource", "uploadfile"])
def test_upload_missing_field(missing, upload_translator, project_locale_a):
    data = {
        "project": project_locale_a.project.slug,
        "locale": project_locale_a.locale.code,
        "resource": "resource_a.po",
        "uploadfile": _po_file(),
    }
    del data[missing]

    response = _post(_pat_client(upload_translator.user), TRANSLATIONS, **data)

    assert response.status_code == 400
    assert missing in response.json()


@pytest.mark.django_db
def test_upload_incompatible_format(upload_translator, project_locale_a, resource_path):
    response = _post(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=resource_path,
        uploadfile=_po_file(contents="irrelevant", name="resource_a.ftl"),
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_upload_oversized_file(upload_translator, project_locale_a, resource_path):
    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents="#" * (5000 * 1000 + 1),
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_upload_file_validated_after_authorization(
    member, project_locale_a, resource_path
):
    """An oversized file from a user without translator rights is a 403, not a 400."""
    response = _upload(
        _pat_client(member.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents="#" * (5000 * 1000 + 1),
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_unparseable_file(upload_translator, project_locale_a, resource_path):
    """Reject malformed files."""
    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents="this is not valid gettext {{{ broken",
    )

    assert response.status_code == 400
    assert response.json()["uploadfile"][0].startswith("Could not parse uploaded file")


@pytest.mark.django_db
def test_upload_file_without_translations(
    upload_translator, project_locale_a, resource_path
):
    """Reject files with no translations, rather than reporting a no-op."""
    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents="# Just a comment\n",
    )

    assert response.status_code == 400
    assert response.json() == {
        "uploadfile": ["No translations found in uploaded file."]
    }


@pytest.mark.django_db
def test_upload_disabled_project(upload_translator, project_locale_a, resource_path):
    project = project_locale_a.project
    project.disabled = True
    project.save()

    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents='msgid "test_key"\nmsgstr "into disabled"',
    )

    assert response.status_code == 404
    assert not Translation.objects.filter(string="into disabled").exists()


@pytest.mark.django_db
def test_upload_private_project_not_visible(
    upload_translator, project_locale_a, resource_path
):
    project = project_locale_a.project
    project.visibility = Project.Visibility.PRIVATE
    project.save()

    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_unknown_locale(upload_translator, project_locale_a):
    response = _post(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project=project_locale_a.project.slug,
        locale="does-not-exist",
        resource="resource_a.po",
        uploadfile=_po_file(),
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_locale_not_enabled_for_project(member, project_locale_a, locale_b):
    locale_b.translators_group.user_set.add(member.user)

    response = _post(
        _pat_client(member.user),
        TRANSLATIONS,
        project=project_locale_a.project.slug,
        locale=locale_b.code,
        resource="resource_a.po",
        uploadfile=_po_file(),
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_unknown_resource(upload_translator, project_locale_a):
    response = _post(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource="does_not_exist.po",
        uploadfile=_po_file(name="does_not_exist.po"),
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_resource_not_enabled_for_locale(
    upload_translator, project_locale_a, resource_a
):
    """A resource with no TranslatedResource for the locale is not writable."""
    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_a.path,
    )

    assert response.status_code == 404
    assert not Translation.objects.filter(entity__resource=resource_a).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("url", ENDPOINTS)
@pytest.mark.parametrize(
    "error",
    [
        IntegrityError("duplicate key value violates unique constraint"),
        UploadConflictError(),
    ],
)
def test_upload_concurrent_conflict(
    monkeypatch, url, error, pretranslator, project_locale_a, resource_path
):
    """A clash with a concurrent upload or review is reported as a conflict."""

    def failing_import(*args, **kwargs):
        raise error

    monkeypatch.setattr(sync_upload, IMPORTERS[url], failing_import)

    response = _upload(
        _pat_client(pretranslator.user), url, project_locale_a, resource_path
    )

    assert response.status_code == 409


# Responses


@pytest.mark.django_db
def test_upload_translations_response(
    upload_translator, project_locale_a, upload_po_translation, resource_path
):
    """The upload is also additive: strings missing from the file are left alone."""
    untouched = _approved_translation(
        project_locale_a, upload_po_translation.entity.resource, "other_key"
    )

    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
    )

    assert response.status_code == 200
    assert response.json() == {
        "updated": 1,
        "unchanged": 0,
        "undefined_keys": [],
        "undefined_keys_count": 0,
        "badge_updates": [],
    }

    translation = Translation.objects.get(string="new translation")

    assert translation.approved
    assert translation.user == upload_translator.user
    assert not translation.warnings.exists()
    assert ActionLog.objects.filter(
        performed_by=upload_translator.user,
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation,
    ).exists()

    untouched.refresh_from_db()
    assert untouched.approved
    assert untouched.active
    assert not untouched.rejected


@pytest.mark.django_db
def test_upload_translations_unchanged(
    upload_translator, project_locale_a, upload_po_translation, resource_path
):
    """Re-uploading a file that changed nothing is reported as unchanged."""
    client = _pat_client(upload_translator.user)
    first = _upload(client, TRANSLATIONS, project_locale_a, resource_path)
    assert first.json()["updated"] == 1

    second = _upload(client, TRANSLATIONS, project_locale_a, resource_path)

    assert second.status_code == 200
    assert second.json()["updated"] == 0
    assert second.json()["unchanged"] == 1
    assert Translation.objects.filter(string="new translation").count() == 1


@pytest.mark.django_db
def test_upload_translations_replaces_approved_translation(
    upload_translator, project_locale_a, upload_po_translation, resource_path
):
    """An uploaded translation replaces the approved one, rejecting it."""
    upload_po_translation.approved = True
    upload_po_translation.active = True
    upload_po_translation.save()

    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 1

    upload_po_translation.refresh_from_db()
    assert not upload_po_translation.approved
    assert upload_po_translation.rejected
    assert (
        Translation.objects.get(
            entity=upload_po_translation.entity, approved=True
        ).string
        == "new translation"
    )


@pytest.mark.django_db
def test_upload_translations_approves_matching_suggestion(
    upload_translator, project_locale_a, upload_po_translation, resource_path
):
    """An upload matching an existing suggestion approves it in place,
    and the entity is still marked as changed for the next sync."""
    assert not upload_po_translation.approved

    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents=f'msgid "test_key"\nmsgstr "{upload_po_translation.string}"',
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 1

    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1
    upload_po_translation.refresh_from_db()
    assert upload_po_translation.approved
    assert ChangedEntityLocale.objects.filter(
        entity=upload_po_translation.entity, locale=project_locale_a.locale
    ).exists()


@pytest.mark.django_db
def test_upload_translations_identical_fuzzy_unchanged(
    upload_translator, project_locale_a, upload_po_translation, resource_path
):
    """An uploaded fuzzy translation matching an existing fuzzy one changes nothing."""
    upload_po_translation.fuzzy = True
    upload_po_translation.active = True
    upload_po_translation.save()

    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents=f'#, fuzzy\nmsgid "test_key"\nmsgstr "{upload_po_translation.string}"',
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 0
    assert response.json()["unchanged"] == 1

    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1
    assert not ChangedEntityLocale.objects.filter(
        entity=upload_po_translation.entity
    ).exists()


@pytest.mark.django_db
def test_upload_translations_approves_matching_fuzzy(
    upload_translator, project_locale_a, upload_po_translation, resource_path
):
    """An uploaded non-fuzzy translation matching an existing fuzzy one approves it."""
    upload_po_translation.fuzzy = True
    upload_po_translation.active = True
    upload_po_translation.save()

    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents=f'msgid "test_key"\nmsgstr "{upload_po_translation.string}"',
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 1

    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1
    upload_po_translation.refresh_from_db()
    assert upload_po_translation.approved
    assert not upload_po_translation.fuzzy


@pytest.mark.django_db
def test_upload_translations_ignores_obsolete_entities(
    upload_translator, project_locale_a, upload_po_translation, resource_path
):
    """A key removed and later re-added leaves an obsolete entity with the same key.
    The upload fills the new, untranslated key and counts it as updated, even though
    the translation matches the one of the obsolete entity."""
    _approved_translation(
        project_locale_a,
        upload_po_translation.entity.resource,
        "test_key",
        string="new translation",
        obsolete=True,
    )

    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 1
    assert (
        Translation.objects.get(
            entity=upload_po_translation.entity, approved=True
        ).string
        == "new translation"
    )


@pytest.mark.django_db
def test_upload_pretranslations_response(
    pretranslator, project_locale_a, untranslated_entity
):
    response = _upload(
        _pat_client(pretranslator.user),
        PRETRANSLATIONS,
        project_locale_a,
        untranslated_entity.resource.path,
        contents='msgid "other_key"\nmsgstr "pretranslation"',
    )

    assert response.status_code == 200
    assert response.json() == {
        "created": 1,
        "replaced": 0,
        "converted": 0,
        "unchanged": 0,
        "skipped": 0,
        "failed_checks": [],
        "failed_checks_count": 0,
        "undefined_keys": [],
        "undefined_keys_count": 0,
        "badge_updates": [],
    }

    translation = Translation.objects.get(entity=untranslated_entity)

    assert translation.pretranslated
    assert translation.user == pretranslator.user


@pytest.mark.django_db
def test_upload_suggestions_response(
    upload_translator, project_locale_a, untranslated_entity
):
    response = _upload(
        _pat_client(upload_translator.user),
        SUGGESTIONS,
        project_locale_a,
        untranslated_entity.resource.path,
        contents='msgid "other_key"\nmsgstr "a suggestion"',
    )

    assert response.status_code == 200
    assert response.json() == {
        "created": 1,
        "restored": 0,
        "unchanged": 0,
        "failed_checks": [],
        "failed_checks_count": 0,
        "undefined_keys": [],
        "undefined_keys_count": 0,
        "badge_updates": [],
    }

    translation = Translation.objects.get(entity=untranslated_entity)

    assert not translation.approved
    assert not translation.pretranslated
    assert translation.user == upload_translator.user


@pytest.mark.django_db
def test_upload_unknown_keys_reported(
    upload_translator, project_locale_a, resource_path
):
    """Unknown keys are reported in the format of entity keys."""
    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents='msgid "test_key"\nmsgstr "new translation"\n\n'
        'msgid "no_such_key"\nmsgstr "x"\n\n'
        'msgid "another_missing"\nmsgstr "y"\n',
    )

    assert response.status_code == 200
    assert response.json() == {
        "updated": 1,
        "unchanged": 0,
        "undefined_keys": [["no_such_key"], ["another_missing"]],
        "undefined_keys_count": 2,
        "badge_updates": [],
    }


@pytest.mark.django_db
def test_upload_unknown_keys_truncated(
    upload_translator, project_locale_a, resource_path
):
    """Report at most UPLOAD_KEYS_ERROR_LIMIT unknown keys, alongside their total number."""
    unknown = 2 * UPLOAD_KEYS_ERROR_LIMIT
    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
        contents="\n\n".join(
            f'msgid "missing_{i}"\nmsgstr "x"' for i in range(unknown)
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["undefined_keys"]) == UPLOAD_KEYS_ERROR_LIMIT
    assert body["undefined_keys_count"] == unknown


@pytest.mark.django_db
@pytest.mark.parametrize("url", [PRETRANSLATIONS, SUGGESTIONS])
def test_upload_failed_checks_reported(
    monkeypatch, url, pretranslator, project_locale_a, resource_path
):
    """Translations left out for failing checks are reported with their messages."""

    def failing_checks(entity, locale_code, string, use_tt_checks):
        return {"pErrors": ["Test error"], "pWarnings": ["Test warning"]}

    monkeypatch.setattr(sync_upload, "run_checks", failing_checks)

    response = _upload(
        _pat_client(pretranslator.user), url, project_locale_a, resource_path
    )

    assert response.status_code == 200
    assert response.json()["created"] == 0
    assert response.json()["failed_checks"] == [
        {"key": ["test_key"], "errors": ["Test error"], "warnings": ["Test warning"]}
    ]
    assert response.json()["failed_checks_count"] == 1


# Badges


@pytest.mark.django_db
@pytest.mark.parametrize("url", ENDPOINTS)
def test_upload_badge_notification(
    monkeypatch, url, pretranslator, project_locale_a, resource_path
):
    """Crossing a badge threshold is reported in the response, and notified."""
    levels = iter([0, 1])
    monkeypatch.setattr(
        badge_utils, "badges_translation_level", lambda user: next(levels)
    )
    monkeypatch.setattr(badge_utils, "badges_review_level", lambda user: 0)

    response = _upload(
        _pat_client(pretranslator.user), url, project_locale_a, resource_path
    )

    assert response.status_code == 200
    assert response.json()["badge_updates"] == [
        {"name": "Translation Champion", "level": 1}
    ]
    notification = Notification.objects.filter(
        recipient=pretranslator.user, data__category="badge"
    ).get()
    assert "Translation Champion" in notification.description


@pytest.mark.django_db
def test_upload_no_badge_notification_below_threshold(
    monkeypatch, upload_translator, project_locale_a, resource_path
):
    """No notification when the upload doesn't move the user to a new badge level."""
    monkeypatch.setattr(badge_utils, "badges_translation_level", lambda user: 1)
    monkeypatch.setattr(badge_utils, "badges_review_level", lambda user: 0)

    response = _upload(
        _pat_client(upload_translator.user),
        TRANSLATIONS,
        project_locale_a,
        resource_path,
    )

    assert response.status_code == 200
    assert response.json()["badge_updates"] == []
    assert not Notification.objects.filter(
        recipient=upload_translator.user, data__category="badge"
    ).exists()


# Throttling


@pytest.mark.django_db
@pytest.mark.parametrize(
    "rates",
    [
        {"upload_burst": "2/minute", "upload_sustained": "1000/hour"},
        {"upload_burst": "60/minute", "upload_sustained": "2/hour"},
    ],
)
def test_upload_throttled(
    monkeypatch, upload_translator, project_locale_a, resource_path, rates
):
    # DRF copies the rates into a class attribute at import time, so overriding the
    # REST_FRAMEWORK setting has no effect here.
    monkeypatch.setattr(SimpleRateThrottle, "THROTTLE_RATES", rates)
    cache.clear()

    client = _pat_client(upload_translator.user)
    for expected_status in (200, 200, 429):
        response = _upload(client, TRANSLATIONS, project_locale_a, resource_path)
        assert response.status_code == expected_status

    cache.clear()


@pytest.mark.django_db
def test_upload_endpoints_share_the_quota(
    monkeypatch, pretranslator, project_locale_a, resource_path
):
    """All uploads count against the same per-user quota."""
    monkeypatch.setattr(
        SimpleRateThrottle,
        "THROTTLE_RATES",
        {"upload_burst": "3/minute", "upload_sustained": "1000/hour"},
    )
    cache.clear()

    client = _pat_client(pretranslator.user)
    for url, expected_status in zip(
        [TRANSLATIONS, PRETRANSLATIONS, SUGGESTIONS, TRANSLATIONS],
        (200, 200, 200, 429),
    ):
        response = _upload(client, url, project_locale_a, resource_path)
        assert response.status_code == expected_status

    cache.clear()
