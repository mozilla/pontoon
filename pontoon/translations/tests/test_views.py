import pytest

from django.urls import reverse

from pontoon.base.models import Translation
from pontoon.checks.models import Warning
from pontoon.test.factories import TranslationFactory


@pytest.yield_fixture
def request_create_translation():
    """
    Return a function to call the create_translation view with default parameters.
    """

    def func(client, **args):
        update_params = {
            "translation": "approved translation",
            "plural_form": "-1",
            "ignore_warnings": "true",
        }
        update_params.update(args)

        return client.post(
            reverse("pontoon.translations.create"),
            update_params,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

    return func


@pytest.mark.django_db
def test_create_translation_success(
    member, entity_a, locale_a, project_locale_a, request_create_translation
):
    content = "Bonjour !"
    response = request_create_translation(
        member.client,
        entity=entity_a.pk,
        original=entity_a.string,
        locale=locale_a.code,
        translation=content,
    )
    assert response.status_code == 200
    assert response.json()["status"]

    assert Translation.objects.filter(
        entity=entity_a, locale=locale_a, string=content
    ).exists()


@pytest.mark.django_db
def test_create_translation_not_logged_in(
    client, entity_a, locale_a, request_create_translation
):
    response = request_create_translation(
        client,
        entity=entity_a.pk,
        original=entity_a.string,
        locale=locale_a.code,
        translation="",
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_translation_force_suggestions(
    project_locale_a, translation_a, locale_a, member, request_create_translation,
):
    """
    Save/suggest button should always do what the current label says and
    be independent from the user settings in different browser tabs.
    """
    translation_a.active = True
    translation_a.save()
    translation_a.locale.translators_group.user_set.add(member.user)
    project_locale_a.unreviewed_strings = 1
    project_locale_a.save()

    response = request_create_translation(
        member.client,
        entity=translation_a.entity.pk,
        original=translation_a.entity.string,
        locale=locale_a.code,
        translation="approved 0",
    )
    assert response.status_code == 200
    assert Translation.objects.last().approved is True

    response = request_create_translation(
        member.client,
        entity=translation_a.entity.pk,
        original=translation_a.entity.string,
        locale=locale_a.code,
        translation="approved translation 0",
        force_suggestions="false",
    )
    assert response.status_code == 200
    assert Translation.objects.last().approved is True

    response = request_create_translation(
        member.client,
        entity=translation_a.entity.pk,
        original=translation_a.entity.string,
        locale=locale_a.code,
        translation="unapproved translation 0",
        force_suggestions="true",
    )
    assert response.status_code == 200
    assert Translation.objects.last().approved is False


@pytest.yield_fixture
def properties_resource(resource_a):
    """
    A resource to trigger Translate Toolkit and compare-locales checks at once.
    """
    resource_a.format = "properties"
    resource_a.path = "test1.properties"
    resource_a.save()

    yield resource_a


@pytest.yield_fixture
def properties_entity(entity_a, properties_resource):
    """
    An entity from properties_resource.
    """
    entity_a.translation_set.all().delete()
    entity_a.string = "something %s"
    entity_a.save()

    yield entity_a


@pytest.mark.django_db
def test_run_checks_during_translation_update(
    properties_entity, member, locale_a, project_locale_a, request_create_translation,
):
    """
    The backend shouldn't allow to post translations with critical errors.
    """
    response = request_create_translation(
        member.client,
        locale=locale_a.code,
        entity=properties_entity.pk,
        translation="bad  suggestion",
        original=properties_entity.string,
        ignore_warnings="false",
    )

    assert response.status_code == 200
    assert response.json() == {
        "failedChecks": {
            "clWarnings": ["trailing argument 1 `s` missing"],
            "ttWarnings": ["Double spaces"],
        },
        "status": False,
    }

    # User decides to ignore checks (but there are errors)
    response = request_create_translation(
        member.client,
        entity=properties_entity.pk,
        original=properties_entity.string,
        locale=locale_a.code,
        translation="bad suggestion \\q %q",
        ignore_warnings="true",
    )

    assert response.status_code == 200
    assert response.json() == {
        "failedChecks": {
            "clErrors": ["Found single %"],
            "clWarnings": ["unknown escape sequence, \\q"],
        },
        "status": False,
    }

    # User decides to ignore checks (there are only warnings)
    response = request_create_translation(
        member.client,
        entity=properties_entity.pk,
        original=properties_entity.string,
        locale=locale_a.code,
        translation="bad suggestion",
        ignore_warnings="true",
    )

    assert response.status_code == 200
    assert response.json()["status"]

    translation_pk = response.json()["translation"]["pk"]
    assert Translation.objects.get(pk=translation_pk).approved is False

    (warning,) = Warning.objects.all()

    assert warning.translation_id == translation_pk
    assert warning.library == "cl"
    assert warning.message == "trailing argument 1 `s` missing"


@pytest.fixture
def approved_translation(locale_a, project_locale_a, entity_a, user_a):
    return TranslationFactory(
        entity=entity_a, locale=locale_a, user=user_a, approved=True, active=True,
    )


@pytest.fixture
def rejected_translation(locale_a, project_locale_a, entity_a, user_a):
    return TranslationFactory(
        entity=entity_a, locale=locale_a, user=user_a, rejected=True
    )


@pytest.mark.django_db
def test_view_translation_delete(approved_translation, rejected_translation, member):
    """Check if delete view works properly."""
    url = reverse("pontoon.translations.delete")
    params = {
        "translation": rejected_translation.pk,
    }

    response = member.client.post(url, params)
    assert response.status_code == 400
    assert response.content == b"Bad Request: Request must be AJAX"

    # Rejected translation gets deleted
    response = member.client.post(url, params, HTTP_X_REQUESTED_WITH="XMLHttpRequest",)
    assert response.status_code == 200
    assert Translation.objects.filter(pk=rejected_translation.pk).exists() is False

    # Approved translation doesn't get deleted
    params = {
        "translation": approved_translation.pk,
    }
    response = member.client.post(url, params, HTTP_X_REQUESTED_WITH="XMLHttpRequest",)
    assert response.status_code == 403
    assert Translation.objects.filter(pk=approved_translation.pk).exists() is True


@pytest.mark.django_db
def test_approve_translation_basic(translation_a, client_superuser):
    """Check if approve view works properly."""
    url = reverse("pontoon.translations.approve")
    params = {
        "translation": translation_a.pk,
        "paths": [],
        "ignore_warnings": "true",
    }

    response = client_superuser.post(url, params)
    assert response.status_code == 400
    assert response.content == b"Bad Request: Request must be AJAX"

    response = client_superuser.post(
        url, params, HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200, response.content

    translation_a.refresh_from_db()
    assert translation_a.approved is True
    assert translation_a.approved_user == response.wsgi_request.user
    assert translation_a.memory_entries.exists() is True


@pytest.mark.django_db
def test_approve_translation_rejects_previous_approved(
    approved_translation, translation_a, client_superuser,
):
    """Check if previously approved translations get rejected on approve."""
    url = reverse("pontoon.translations.approve")
    params = {
        "translation": translation_a.pk,
        "paths": [],
        "ignore_warnings": "true",
    }

    response = client_superuser.post(
        url, params, HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200, response.content
    approved_translation.refresh_from_db()

    translation_a.refresh_from_db()
    assert translation_a.approved is True
    assert translation_a.active is True
    assert approved_translation.approved is False
    assert approved_translation.active is False
    assert approved_translation.rejected is True
    assert approved_translation.rejected_user == response.wsgi_request.user


@pytest.mark.django_db
def test_unapprove_translation(approved_translation, member):
    """Check if unapprove view works properly."""
    url = reverse("pontoon.translations.unapprove")
    params = {
        "translation": approved_translation.pk,
        "paths": [],
    }

    response = member.client.post(url, params)
    assert response.status_code == 400
    assert response.content == b"Bad Request: Request must be AJAX"

    response = member.client.post(url, params, HTTP_X_REQUESTED_WITH="XMLHttpRequest",)
    assert response.status_code == 200

    approved_translation.refresh_from_db()
    assert approved_translation.approved is False
    assert approved_translation.unapproved_user == response.wsgi_request.user
