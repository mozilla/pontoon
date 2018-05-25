import pytest

from django.urls import reverse


def test_batch_edit_translations_no_user(client):
    """If there are no logged in users, the view redirects to the login page.
    """
    response = client.post(reverse('pontoon.batch.edit.translations'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_batch_edit_translations_bad_request(client, member, locale_a):
    # No `locale` parameter.
    response = client.post(
        reverse('pontoon.batch.edit.translations'),
        {'action': 'reject'},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 400
    assert 'locale' in response.content

    # No `action` parameter.
    response = client.post(
        reverse('pontoon.batch.edit.translations'),
        {'locale': locale_a.code},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 400
    assert 'action' in response.content

    # Incorrect `action` parameter.
    response = client.post(
        reverse('pontoon.batch.edit.translations'),
        {'action': 'unknown', 'locale': locale_a.code},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 400
    assert 'action' in response.content

    # Incorrect `locale` parameter.
    response = client.post(
        reverse('pontoon.batch.edit.translations'),
        {'action': 'reject', 'locale': 'unknown'},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 404
    assert 'action' in response.content


@pytest.mark.django_db
def test_batch_edit_translations_no_permissions(
    client, member, locale_a, entity_a, project_locale_a
):
    response = client.post(
        reverse('pontoon.batch.edit.translations'),
        {
            'action': 'reject',
            'locale': locale_a.code,
            'entities': entity_a.id,
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 403
    assert 'Forbidden' in response.content
