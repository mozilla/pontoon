import json

import pytest

from mock import patch

from pontoon.base.models import Entity, TranslatedResource
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    UserFactory,
)


@pytest.fixture
def user_a():
    return UserFactory(
        username="user_a",
        email="user_a@example.org"
    )


@pytest.fixture
def member(client, user_a):
    """Provides a `LoggedInMember` with the attributes `user` and `client`
    the `client` is authenticated
    """

    class LoggedInMember(object):

        def __init__(self, user, client):
            client.force_login(user)
            self.client = client
            self.user = user

    return LoggedInMember(user_a, client)


@pytest.fixture
def locale_a():
    return LocaleFactory(
        code="kg",
        name="Klingon",
    )


@pytest.fixture
def project_a():
    return ProjectFactory(
        slug="project_a", name="Project A", repositories=[],
    )


@pytest.fixture
def project_locale_a(project_a, locale_a):
    return ProjectLocaleFactory(
        project=project_a,
        locale=locale_a,
    )


@pytest.fixture
def resource_a(locale_a, project_a):
    return ResourceFactory(
        project=project_a, path="resource_a.po", format="po"
    )


@pytest.fixture
def entity_a(resource_a, project_locale_a):
    return EntityFactory(
        resource=resource_a, string="entity"
    )


@pytest.mark.django_db
def test_view_entity_inplace_mode(
    member,
    resource_a,
    locale_a,
):
    """
    Inplace mode of get_entites, should return all entities in a single batch.
    """
    TranslatedResourceFactory.create(resource=resource_a, locale=locale_a)
    entities = EntityFactory.create_batch(size=3, resource=resource_a)
    entities_pks = [e.pk for e in entities]
    response = member.client.post(
        '/get-entities/',
        {
            'project': resource_a.project.slug,
            'locale': locale_a.code,
            'paths[]': [resource_a.path],
            'inplace_editor': True,
            # Inplace mode shouldn't respect paging or limiting page
            'limit': 1,
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 200
    assert json.loads(response.content)["has_next"] is False
    assert (
        sorted([e['pk'] for e in json.loads(response.content)['entities']])
        == sorted(entities_pks)
    )


@pytest.mark.django_db
def test_view_entity_filters(member, resource_a, locale_a):
    """
    Tests if right filter calls right method in the Entity manager.
    """
    filters = (
        'missing',
        'fuzzy',
        'suggested',
        'translated',
        'unchanged',
        'has-suggestions',
        'rejected',
    )
    for filter_ in filters:
        filter_name = filter_.replace('-', '_')
        params = {
            'project': resource_a.project.slug,
            'locale': locale_a.code,
            'paths[]': [resource_a.path],
            'limit': 1,
        }
        if filter_ in ('unchanged', 'has-suggestions', 'rejected'):
            params['extra'] = filter_
        else:
            params['status'] = filter_
        patched_entity = patch(
            'pontoon.base.models.Entity.objects.{}'.format(filter_name)
        )
        with patched_entity as m:
            m.return_value = getattr(Entity.objects, filter_name)(locale_a)
            member.client.post(
                '/get-entities/',
                params,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            )
            assert m.called is True


@pytest.mark.django_db
def test_view_entity_exclude_entities(
    member,
    resource_a,
    locale_a,
):
    """
    Excluded entities shouldn't be returned by get_entities.
    """
    TranslatedResource.objects.create(resource=resource_a, locale=locale_a)
    entities = EntityFactory.create_batch(size=3, resource=resource_a)
    response = member.client.post(
        '/get-entities/',
        {
            'project': resource_a.project.slug,
            'locale': locale_a.code,
            'paths[]': [resource_a.path],
            'exclude_entities': [entities[1].pk],
            'limit': 1,
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 200
    assert json.loads(response.content)["has_next"] is True
    assert (
        [e['pk'] for e in json.loads(response.content)['entities']]
        == [entities[2].pk]
    )

    exclude_entities = ','.join(map(
        str,
        [
            entities[2].pk,
            entities[1].pk,
        ]
    ))
    response = member.client.post(
        '/get-entities/',
        {
            'project': resource_a.project.slug,
            'locale': locale_a.code,
            'paths[]': [resource_a.path],
            'exclude_entities': exclude_entities,
            'limit': 1,
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 200
    assert json.loads(response.content)["has_next"] is False
    assert (
        [e['pk'] for e in json.loads(response.content)['entities']]
        == [entities[0].pk]
    )
