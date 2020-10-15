import pytest

from django.urls import reverse

from pontoon.checks.utils import bulk_run_checks
from pontoon.test.factories import TranslationFactory, ProjectLocaleFactory


@pytest.yield_fixture
def batch_action(client, admin_client):
    """
    Shortcut function to make API-call more readable in tests.
    """

    def _action(admin=False, **opts):
        """
        :param bool admin: when true then uses admin_client to make api calls.
        :param opts: options passed to the batch action view.
        """
        if admin:
            client_ = admin_client
        else:
            client_ = client

        response = client_.post(
            reverse("pontoon.batch.edit.translations"),
            opts,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        return response

    return _action


@pytest.yield_fixture
def translation_dtd_unapproved():
    translation = TranslationFactory.create(
        string="Test Translation",
        active=True,
        approved=False,
        entity__key="test",
        entity__resource__format="dtd",
        entity__resource__path="test.dtd",
    )
    bulk_run_checks([translation])

    ProjectLocaleFactory.create(
        project=translation.entity.resource.project, locale=translation.locale,
    )

    yield translation


@pytest.yield_fixture
def translation_dtd_invalid_unapproved():
    # Provide invalid characters in translation to cause checks to fail
    translation = TranslationFactory.create(
        string='!@#$""\'',
        active=True,
        approved=False,
        entity__key="test",
        entity__resource__format="dtd",
        entity__resource__path="test.dtd",
    )
    bulk_run_checks([translation])

    ProjectLocaleFactory.create(
        project=translation.entity.resource.project, locale=translation.locale,
    )

    yield translation


@pytest.yield_fixture
def test_batch_edit_translations_no_user(client):
    """If there are no logged in users, the view redirects to the login page.
    """
    response = client.post(reverse("pontoon.batch.edit.translations"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_batch_edit_translations_bad_request(batch_action, member, locale_a):
    # No `locale` parameter.
    response = batch_action(action="reject")
    assert response.status_code == 400
    assert b"locale" in response.content

    # No `action` parameter.
    response = batch_action(locale=locale_a.code)
    assert response.status_code == 400
    assert b"action" in response.content

    # Incorrect `action` parameter.
    response = batch_action(action="unknown", locale=locale_a.code,)

    assert response.status_code == 400
    assert b"action" in response.content


@pytest.mark.django_db
def test_batch_edit_translations_not_found(batch_action, member, locale_a):
    # Incorrect `locale` parameter.
    response = batch_action(action="reject", locale="unknown",)
    assert response.status_code == 404


@pytest.mark.django_db
def test_batch_edit_translations_no_permissions(
    batch_action, member, locale_a, entity_a, project_locale_a
):
    response = batch_action(
        action="reject", locale=locale_a.code, entities=entity_a.id,
    )

    assert response.status_code == 403
    assert b"Forbidden" in response.content


@pytest.mark.django_db
def test_batch_approve_valid_translations(
    batch_action, member, translation_dtd_unapproved,
):
    """
    Approve translations without errors.
    """
    response = batch_action(
        admin=True,
        action="approve",
        locale=translation_dtd_unapproved.locale.code,
        entities=translation_dtd_unapproved.entity.pk,
    )
    assert response.json() == {
        "count": 1,
        "invalid_translation_count": 0,
    }

    translation_dtd_unapproved.refresh_from_db()
    assert translation_dtd_unapproved.approved


@pytest.mark.django_db
def test_batch_approve_invalid_translations(
    batch_action, member, translation_dtd_invalid_unapproved,
):
    """
    Translations with errors can't be approved.
    """

    response = batch_action(
        admin=True,
        action="approve",
        locale=translation_dtd_invalid_unapproved.locale.code,
        entities=translation_dtd_invalid_unapproved.entity.pk,
    )

    assert response.json() == {
        "count": 0,
        "invalid_translation_count": 1,
    }

    translation_dtd_invalid_unapproved.refresh_from_db()

    assert not translation_dtd_invalid_unapproved.approved


@pytest.mark.django_db
def test_batch_find_and_replace_valid_translations(
    batch_action, member, translation_dtd_unapproved,
):
    response = batch_action(
        admin=True,
        action="replace",
        locale=translation_dtd_unapproved.locale.code,
        entities=translation_dtd_unapproved.entity.pk,
        find="Translation",
        replace="Replaced translation",
    )

    assert response.json() == {
        "count": 1,
        "invalid_translation_count": 0,
    }

    translation = translation_dtd_unapproved.entity.translation_set.last()

    assert translation.string == "Test Replaced translation"
    assert translation.approved


@pytest.mark.django_db
def test_batch_find_and_replace_invalid_translations(
    batch_action, member, translation_dtd_unapproved,
):
    """
    The `find & replace` action can't produce invalid translations.
    """
    response = batch_action(
        admin=True,
        action="replace",
        locale=translation_dtd_unapproved.locale.code,
        entities=translation_dtd_unapproved.entity.pk,
        find="Translation",
        replace="%$#%>",
    )

    assert response.json() == {
        "count": 0,
        "invalid_translation_count": 1,
    }

    translation = translation_dtd_unapproved.entity.translation_set.last()

    assert translation.string == "Test Translation"
    assert not translation.approved
