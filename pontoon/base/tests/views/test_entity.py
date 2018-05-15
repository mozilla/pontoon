
import json

import pytest

from mock import patch

from pontoon.base.models import Entity, TranslatedResource


@pytest.mark.django_db
def test_view_entity_inplace_mode(member0, resourceX, localeX,
                                  entity_factory):
    """
    Inplace mode of get_entites, should return all entities in a single batch.
    """
    TranslatedResource.objects.create(resource=resourceX, locale=localeX)
    entities = entity_factory(resource=resourceX, batch=3)
    entities_pks = [e.pk for e in entities]
    response = member0.client.post(
        '/get-entities/',
        {'project': resourceX.project.slug,
         'locale': localeX.code,
         'paths[]': [resourceX.path],
         'inplace_editor': True,
         # Inplace mode shouldn't respect paging or limiting page
         'limit': 1},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    assert json.loads(response.content)["has_next"] is False
    assert (
        [e['pk'] for e in json.loads(response.content)['entities']]
        == entities_pks)


@pytest.mark.skip('Mocking of the methods is now very hard.')
@pytest.mark.django_db
def test_view_entity_filters(member0, resource0, locale0, entity_factory):
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
        'rejected')
    for filter_ in filters:
        filter_name = filter_.replace('-', '_')
        params = {
            'project': resource0.project.slug,
            'locale': locale0.code,
            'paths[]': [resource0.path],
            'limit': 1}
        if filter_ in ('unchanged', 'has-suggestions', 'rejected'):
            params['extra'] = filter_
        else:
            params['status'] = filter_
        patched_entity = patch(
            'pontoon.base.models.Entity.objects.{}'.format(filter_name))
        with patched_entity as m:
            m.return_value = getattr(Entity.objects, filter_name)(locale0)
            member0.client.post(
                '/get-entities/',
                params,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            assert m.called is True


@pytest.mark.django_db
def test_view_entity_exclude_entities(member0, resourceX, localeX,
                                      entity_factory):
    """
    Excluded entities shouldn't returned by get_entities.
    """
    TranslatedResource.objects.create(resource=resourceX, locale=localeX)
    entities = entity_factory(resource=resourceX, batch=3)
    response = member0.client.post(
        '/get-entities/',
        {'project': resourceX.project.slug,
         'locale': localeX.code,
         'paths[]': [resourceX.path],
         'exclude_entities': [entities[1].pk],
         'limit': 1},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    assert json.loads(response.content)["has_next"] is True
    assert (
        [e['pk'] for e in json.loads(response.content)['entities']]
        == [entities[0].pk])

    exclude_entities = ','.join(
        map(str,
            [entities[0].pk,
             entities[1].pk]))
    response = member0.client.post(
        '/get-entities/',
        {'project': resourceX.project.slug,
         'locale': localeX.code,
         'paths[]': [resourceX.path],
         'exclude_entities': exclude_entities,
         'limit': 1},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    assert json.loads(response.content)["has_next"] is False
    assert (
        [e['pk'] for e in json.loads(response.content)['entities']]
        == [entities[2].pk])
