import pytest

from rest_framework.test import APIClient

from django.contrib.auth.models import User

from pontoon.base.models import Translation
from pontoon.test.factories import EntityFactory, TranslationFactory


SUBMIT_URL = "/api/v2/translations/"
APPROVE_URL = "/api/v2/translations/approve/"
REJECT_URL = "/api/v2/translations/reject/"
UNAPPROVE_URL = "/api/v2/translations/unapprove/"
DELETE_URL = "/api/v2/translations/delete/"


def api_client(user=None):
    client = APIClient()
    if user is not None:
        client.force_authenticate(user=user)
    return client


def as_privileged(user, locale):
    """Grant translate/review rights on `locale` (locale-manager path, which
    bypasses ProjectLocale.has_custom_translators) and return a freshly loaded
    user so no stale permission cache carries over — mirroring how the real
    PAT-authenticated request loads its user from the database each call.
    """
    locale.managers_group.user_set.add(user)
    return User.objects.get(pk=user.pk)


@pytest.fixture
def gettext_entity(resource_a):
    """A gettext entity in project_a with an explicit key."""
    return EntityFactory(resource=resource_a, key=["greeting"], string="entity a")


def submit_item(entity, locale, value=None, **overrides):
    item = {
        "project": entity.resource.project.slug,
        "resource": entity.resource.path,
        "key": entity.key,
        "locale": locale.code,
        "value": value if value is not None else ["Bonjour"],
        "ignore_warnings": True,
    }
    item.update(overrides)
    return item


# --- Submit / create ---------------------------------------------------------


@pytest.mark.django_db
def test_submit_requires_authentication(gettext_entity, locale_a, project_locale_a):
    response = api_client().post(
        SUBMIT_URL, submit_item(gettext_entity, locale_a), format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_submit_as_translator_creates_approved(
    member, gettext_entity, locale_a, project_locale_a
):
    user = as_privileged(member.user, locale_a)
    response = api_client(user).post(
        SUBMIT_URL, submit_item(gettext_entity, locale_a), format="json"
    )
    assert response.status_code == 200
    assert response.data["status"] == "created", response.data

    translation = Translation.objects.get(entity=gettext_entity, locale=locale_a)
    assert translation.approved is True
    assert translation.active is True


@pytest.mark.django_db
def test_submit_as_non_translator_creates_suggestion(
    member, gettext_entity, locale_a, project_locale_a
):
    response = api_client(member.user).post(
        SUBMIT_URL, submit_item(gettext_entity, locale_a), format="json"
    )
    assert response.status_code == 200
    assert response.data["status"] == "created"

    translation = Translation.objects.get(entity=gettext_entity, locale=locale_a)
    assert translation.approved is False


@pytest.mark.django_db
def test_submit_force_suggestions_overrides_approval(
    member, gettext_entity, locale_a, project_locale_a
):
    user = as_privileged(member.user, locale_a)
    response = api_client(user).post(
        SUBMIT_URL,
        submit_item(gettext_entity, locale_a, force_suggestions=True),
        format="json",
    )
    assert response.status_code == 200
    assert response.data["status"] == "created"

    translation = Translation.objects.get(entity=gettext_entity, locale=locale_a)
    assert translation.approved is False


@pytest.mark.django_db
def test_submit_single_returns_object_not_list(
    member, gettext_entity, locale_a, project_locale_a
):
    response = api_client(member.user).post(
        SUBMIT_URL, submit_item(gettext_entity, locale_a), format="json"
    )
    assert response.status_code == 200
    assert isinstance(response.data, dict)


@pytest.mark.django_db
def test_submit_bulk_partial_success(
    member, gettext_entity, locale_a, project_locale_a
):
    user = as_privileged(member.user, locale_a)
    good = submit_item(gettext_entity, locale_a, value=["Bonjour"])
    bad = submit_item(gettext_entity, locale_a, value=["Salut"], project="nonexistent")

    response = api_client(user).post(SUBMIT_URL, [good, bad], format="json")
    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert response.data[0]["status"] == "created"
    assert response.data[1]["status"] == "error"

    # Only the good item is persisted.
    assert (
        Translation.objects.filter(entity=gettext_entity, locale=locale_a).count() == 1
    )


@pytest.mark.django_db
def test_submit_dedup_returns_same(
    member, gettext_entity, locale_a, project_locale_a
):
    user = as_privileged(member.user, locale_a)
    client = api_client(user)

    first = client.post(
        SUBMIT_URL, submit_item(gettext_entity, locale_a), format="json"
    )
    assert first.data["status"] == "created"

    second = client.post(
        SUBMIT_URL, submit_item(gettext_entity, locale_a), format="json"
    )
    assert second.data["status"] == "same"
    assert (
        Translation.objects.filter(entity=gettext_entity, locale=locale_a).count() == 1
    )


@pytest.mark.django_db
def test_submit_entity_not_found(member, resource_a, locale_a, project_locale_a):
    item = {
        "project": resource_a.project.slug,
        "resource": resource_a.path,
        "key": ["does-not-exist"],
        "locale": locale_a.code,
        "value": ["Bonjour"],
        "ignore_warnings": True,
    }
    response = api_client(member.user).post(SUBMIT_URL, item, format="json")
    assert response.status_code == 200
    assert response.data["status"] == "error"
    assert "not found" in " ".join(response.data["errors"]).lower()


@pytest.mark.django_db
def test_submit_locale_not_in_project(member, gettext_entity, locale_b):
    # locale_b has no ProjectLocale for project_a -> clean error, not a 500.
    response = api_client(member.user).post(
        SUBMIT_URL, submit_item(gettext_entity, locale_b), format="json"
    )
    assert response.status_code == 200
    assert response.data["status"] == "error"


# --- Review (approve / reject / unapprove / delete) --------------------------


@pytest.fixture
def suggestion(gettext_entity, locale_a, project_locale_a, user_b):
    return TranslationFactory(
        entity=gettext_entity,
        locale=locale_a,
        user=user_b,
        string="Bonjour",
        value=["Bonjour"],
        approved=False,
        active=True,
    )


@pytest.mark.django_db
def test_review_requires_authentication(suggestion):
    response = api_client().post(
        APPROVE_URL, {"translation_id": suggestion.pk}, format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_approve_by_translation_id(member, suggestion, locale_a):
    user = as_privileged(member.user, locale_a)
    response = api_client(user).post(
        APPROVE_URL,
        {"translation_id": suggestion.pk, "ignore_warnings": True},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["status"] == "approved", response.data

    suggestion.refresh_from_db()
    assert suggestion.approved is True


@pytest.mark.django_db
def test_approve_by_coordinates(member, gettext_entity, suggestion, locale_a):
    user = as_privileged(member.user, locale_a)
    response = api_client(user).post(
        APPROVE_URL,
        {
            "project": gettext_entity.resource.project.slug,
            "resource": gettext_entity.resource.path,
            "key": gettext_entity.key,
            "locale": locale_a.code,
            "value": ["Bonjour"],
            "ignore_warnings": True,
        },
        format="json",
    )
    assert response.data["status"] == "approved", response.data

    suggestion.refresh_from_db()
    assert suggestion.approved is True


@pytest.mark.django_db
def test_approve_without_permission_errors(member, suggestion):
    response = api_client(member.user).post(
        APPROVE_URL,
        {"translation_id": suggestion.pk, "ignore_warnings": True},
        format="json",
    )
    assert response.data["status"] == "error"

    suggestion.refresh_from_db()
    assert suggestion.approved is False


@pytest.mark.django_db
def test_reject_suggestion(member, suggestion, locale_a):
    user = as_privileged(member.user, locale_a)
    response = api_client(user).post(
        REJECT_URL, {"translation_id": suggestion.pk}, format="json"
    )
    assert response.data["status"] == "rejected", response.data

    suggestion.refresh_from_db()
    assert suggestion.rejected is True


@pytest.mark.django_db
def test_unapprove_translation(member, suggestion, locale_a):
    user = as_privileged(member.user, locale_a)
    suggestion.approve(user)

    response = api_client(user).post(
        UNAPPROVE_URL, {"translation_id": suggestion.pk}, format="json"
    )
    assert response.data["status"] == "unapproved", response.data

    suggestion.refresh_from_db()
    assert suggestion.approved is False


@pytest.mark.django_db
def test_delete_rejected_translation(member, suggestion, locale_a):
    user = as_privileged(member.user, locale_a)
    suggestion.reject(user)

    response = api_client(user).post(
        DELETE_URL, {"translation_id": suggestion.pk}, format="json"
    )
    assert response.data["status"] == "deleted", response.data
    assert not Translation.objects.filter(pk=suggestion.pk).exists()


@pytest.mark.django_db
def test_delete_non_rejected_errors(member, suggestion, locale_a):
    user = as_privileged(member.user, locale_a)
    response = api_client(user).post(
        DELETE_URL, {"translation_id": suggestion.pk}, format="json"
    )
    assert response.data["status"] == "error"
    assert Translation.objects.filter(pk=suggestion.pk).exists()
