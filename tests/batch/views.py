import pytest

from django.urls import reverse


def test_batch_edit_translations_no_user(client):
    """If there are no logged in users, the view redirects to the login page.
    """
    response = client.post(reverse('pontoon.batch.edit.translations'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_batch_edit_translations_bad_request(client, member0, locale0):
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
        {'locale': locale0.code},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 400
    assert 'action' in response.content

    # Incorrect `action` parameter.
    response = client.post(
        reverse('pontoon.batch.edit.translations'),
        {'action': 'unknown', 'locale': locale0.code},
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
    client, member0, locale0, entity0
):
    response = client.post(
        reverse('pontoon.batch.edit.translations'),
        {
            'action': 'reject',
            'locale': locale0.code,
            'entities': entity0.id,
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 403
    assert 'Forbidden' in response.content
