from __future__ import absolute_import

import pytest

from django.urls import reverse

from pontoon.base.models import Translation
from pontoon.test.factories import (
    ProjectFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslationFactory,
    TranslatedResourceFactory,
)


@pytest.fixture
def approved_translation(locale_a, project_locale_a, entity_a, user_a):
    return TranslationFactory(
        entity=entity_a,
        locale=locale_a,
        user=user_a,
        approved=True,
        active=True,
    )


@pytest.fixture
def rejected_translation(locale_a, project_locale_a, entity_a, user_a):
    return TranslationFactory(
        entity=entity_a, locale=locale_a, user=user_a, rejected=True
    )


@pytest.mark.django_db
def test_approve_translation_basic(translation_a, client_superuser):
    """Check if approve view works properly."""
    url = reverse('pontoon.approve_translation')
    params = {
        'translation': translation_a.pk,
        'paths': [],
        'ignore_warnings': 'true',
    }
    response = client_superuser.post(url, params)
    assert response.status_code == 400
    assert response.content == 'Bad Request: Request must be AJAX'

    response = client_superuser.post(
        url, params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 200, response.content
    translation_a.refresh_from_db()
    assert translation_a.approved is True
    assert translation_a.approved_user == response.wsgi_request.user


@pytest.mark.django_db
def test_approve_translation_rejects_previous_approved(
    approved_translation,
    translation_a,
    client_superuser,
):
    """Check if approve view works properly."""
    url = reverse('pontoon.approve_translation')
    params = {
        'translation': translation_a.pk,
        'paths': [],
        'ignore_warnings': 'true',
    }

    response = client_superuser.post(
        url, params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
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
def test_view_translation_unapprove(approved_translation, member):
    """Check if unapprove view works properly."""
    url = reverse('pontoon.unapprove_translation')
    params = {
        'translation': approved_translation.pk,
        'paths': [],
    }

    response = member.client.post(url, params)
    assert response.status_code == 400
    assert response.content == 'Bad Request: Request must be AJAX'

    response = member.client.post(
        url,
        params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 200

    approved_translation.refresh_from_db()
    assert approved_translation.approved is False
    assert approved_translation.unapproved_user == response.wsgi_request.user


@pytest.mark.django_db
def test_view_translation_delete(approved_translation, rejected_translation, member):
    """Check if delete view works properly."""
    url = reverse('pontoon.delete_translation')
    params = {
        'translation': rejected_translation.pk,
    }

    response = member.client.post(url, params)
    assert response.status_code == 400
    assert response.content == 'Bad Request: Request must be AJAX'

    # Rejected translation gets deleted
    response = member.client.post(
        url,
        params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 200
    assert Translation.objects.filter(pk=rejected_translation.pk).exists() is False

    # Approved translation doesn't get deleted
    params = {
        'translation': approved_translation.pk,
    }
    response = member.client.post(
        url,
        params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 403
    assert Translation.objects.filter(pk=approved_translation.pk).exists() is True


@pytest.mark.django_db
def test_view_translate_invalid_locale_project(client, settings_debug):
    """If the locale and project are both invalid, return a 404."""
    response = client.get('/invalid-locale/invalid-project/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_locale(client, resource_a, settings_debug):
    """
    If the project is valid but the locale isn't, redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        '/invalid-locale/%s/%s/'
        % (resource_a.project.slug, resource_a.path)
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_project(
    client,
    resource_a,
    locale_a,
    settings_debug,
):
    """If the project is invalid, redirect home."""
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        '/%s/invalid-project/%s/'
        % (locale_a.code, resource_a.path)
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_pl(
    client,
    locale_a,
    project_b,
    settings_debug,
):
    """
    If the requested locale is not available for this project,
    redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        '/%s/%s/path/'
        % (locale_a.code, project_b.slug)
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_not_authed_public_project(
    client,
    locale_a,
    settings_debug,
):
    """
    If the user is not authenticated and we're translating project
    ID 1, return a 200.
    """
    project = ProjectFactory.create(slug='valid-project')
    ProjectLocaleFactory.create(
        project=project, locale=locale_a,
    )
    resource = ResourceFactory.create(
        project=project,
        path='foo.lang',
        total_strings=1,
    )
    TranslatedResourceFactory.create(
        resource=resource, locale=locale_a,
    )
    response = client.get(
        '/%s/%s/%s/'
        % (locale_a.code, project.slug, resource.path)
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_translate_force_suggestions(
    project_locale_a,
    translation_a,
    locale_a,
    member,
    request_update_translation,
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

    response = request_update_translation(
        member.client,
        entity=translation_a.entity.pk,
        original=translation_a.entity.string,
        locale=locale_a.code,
        translation='approved 0',
    )
    assert response.status_code == 200
    assert Translation.objects.last().approved is True

    response = request_update_translation(
        member.client,
        entity=translation_a.entity.pk,
        original=translation_a.entity.string,
        locale=locale_a.code,
        translation='approved translation 0',
        force_suggestions='false',
    )
    assert response.status_code == 200
    assert Translation.objects.last().approved is True

    response = request_update_translation(
        member.client,
        entity=translation_a.entity.pk,
        original=translation_a.entity.string,
        locale=locale_a.code,
        translation='unapproved translation 0',
        force_suggestions='true',
    )
    assert response.status_code == 200
    assert Translation.objects.last().approved is False
