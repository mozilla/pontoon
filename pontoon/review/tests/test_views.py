from __future__ import absolute_import, unicode_literals

import pytest

from django.urls import reverse

from pontoon.test.factories import TranslationFactory


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
    url = reverse('pontoon.review.approve')
    params = {
        'translation': translation_a.pk,
        'paths': [],
        'ignore_warnings': 'true',
    }

    response = client_superuser.post(url, params)
    assert response.status_code == 400
    assert response.content == b'Bad Request: Request must be AJAX'

    response = client_superuser.post(
        url, params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 200, response.content

    translation_a.refresh_from_db()
    assert translation_a.approved is True
    assert translation_a.approved_user == response.wsgi_request.user
    assert translation_a.memory_entries.exists() is True


@pytest.mark.django_db
def test_approve_translation_rejects_previous_approved(
    approved_translation,
    translation_a,
    client_superuser,
):
    """Check if previously approved translations get rejected on approve."""
    url = reverse('pontoon.review.approve')
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
def test_unapprove_translation(approved_translation, member):
    """Check if unapprove view works properly."""
    url = reverse('pontoon.review.unapprove')
    params = {
        'translation': approved_translation.pk,
        'paths': [],
    }

    response = member.client.post(url, params)
    assert response.status_code == 400
    assert response.content == b'Bad Request: Request must be AJAX'

    response = member.client.post(
        url,
        params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 200

    approved_translation.refresh_from_db()
    assert approved_translation.approved is False
    assert approved_translation.unapproved_user == response.wsgi_request.user
