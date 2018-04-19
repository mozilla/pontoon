import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from pontoon.base.models import (
    Entity,
    Group,
    Locale,
    Project,
    ProjectLocale,
    Resource,
)


@pytest.fixture
def fakeuser():
    return get_user_model().objects.create(
        username="fakeuser",
        email="fakeuser@example.org"
    )


@pytest.fixture
def member(client, fakeuser):
    """Provides a `LoggedInMember` with the attributes `user` and `client`
    the `client` is authenticated
    """

    class LoggedInMember(object):

        def __init__(self, user, client):
            client.force_login(user)
            self.client = client
            self.user = user

    return LoggedInMember(fakeuser, client)


@pytest.fixture
def locale():
    translators_group = Group.objects.create(
        name='locale translators',
    )
    managers_group = Group.objects.create(
        name='locale managers',
    )
    return Locale.objects.create(
        code="kg",
        name="Klingon",
        translators_group=translators_group,
        managers_group=managers_group,
    )


@pytest.fixture
def entity(locale):
    project = Project.objects.create(
        slug="project", name="Project"
    )
    ProjectLocale.objects.create(project=project, locale=locale)
    resource = Resource.objects.create(
        project=project, path="resource.po", format="po"
    )
    return Entity.objects.create(
        resource=resource, string="entity"
    )


def test_batch_edit_translations_no_user(client):
    """If there are no logged in users, the view redirects to the login page.
    """
    response = client.post(reverse('pontoon.batch.edit.translations'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_batch_edit_translations_bad_request(client, member, locale):
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
        {'locale': locale.code},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 400
    assert 'action' in response.content

    # Incorrect `action` parameter.
    response = client.post(
        reverse('pontoon.batch.edit.translations'),
        {'action': 'unknown', 'locale': locale.code},
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
    client, member, locale, entity
):
    response = client.post(
        reverse('pontoon.batch.edit.translations'),
        {
            'action': 'reject',
            'locale': locale.code,
            'entities': entity.id,
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 403
    assert 'Forbidden' in response.content
