import json

from unittest.mock import patch

import pytest

from pontoon.base.models import Entity, TranslatedResource
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    TranslationFactory,
)


@pytest.mark.django_db
def test_view_entity_filters(member, resource_a, locale_a):
    """
    Tests if right filter calls right method in the Entity manager.
    """
    filters = (
        "missing",
        "fuzzy",
        "unreviewed",
        "translated",
        "unchanged",
        "rejected",
    )
    for filter_ in filters:
        filter_name = filter_.replace("-", "_")
        params = {
            "project": resource_a.project.slug,
            "locale": locale_a.code,
            "paths[]": [resource_a.path],
            "limit": 1,
        }
        if filter_ in ("unchanged", "has-suggestions", "rejected"):
            params["extra"] = filter_
        else:
            params["status"] = filter_
        patched_entity = patch(f"pontoon.base.models.Entity.objects.{filter_name}")
        with patched_entity as m:
            m.return_value = getattr(Entity.objects, filter_name)(locale_a)
            member.client.post(
                "/get-entities/",
                params,
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
            assert m.called is True


@pytest.mark.django_db
def test_view_get_entities_paging(
    member,
    resource_a,
    locale_a,
):
    """
    Only entities from the requested page should be returned by get_entities().
    """
    TranslatedResource.objects.create(resource=resource_a, locale=locale_a)
    ProjectLocaleFactory.create(project=resource_a.project, locale=locale_a)
    entities = EntityFactory.create_batch(size=3, resource=resource_a)

    response = member.client.post(
        "/get-entities/",
        {
            "project": resource_a.project.slug,
            "locale": locale_a.code,
            "paths[]": [resource_a.path],
            "page": 1,
            "limit": 1,
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200
    assert json.loads(response.content)["has_next"] is True
    assert json.loads(response.content)["entities"][0]["pk"] == entities[0].pk

    response = member.client.post(
        "/get-entities/",
        {
            "project": resource_a.project.slug,
            "locale": locale_a.code,
            "paths[]": [resource_a.path],
            "page": len(entities),
            "limit": 1,
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200
    assert json.loads(response.content)["has_next"] is False
    assert json.loads(response.content)["entities"][0]["pk"] == entities[-1].pk


@pytest.mark.django_db
def test_entities_string_not_shown_if_not_matching_filters(member, entity_a, locale_a):
    """
    Test that a string is not displayed if it doesn't match the active filters.
    Regression test for https://github.com/mozilla/pontoon/issues/3148
    """
    ProjectLocaleFactory.create(project=entity_a.resource.project, locale=locale_a)
    TranslatedResource.objects.create(resource=entity_a.resource, locale=locale_a)
    entity_a.resource.total_strings = 1
    entity_a.resource.save()

    TranslationFactory.create(entity=entity_a, locale=locale_a, approved=True)

    response = member.client.post(
        "/get-entities/",
        {
            "project": entity_a.resource.project.slug,
            "locale": locale_a.code,
            "paths[]": [entity_a.resource.path],
            "status": "missing",
            "entity": entity_a.pk,
            "page": 1,
            "limit": 50,
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    data = json.loads(response.content)
    entity_pks = [e["pk"] for e in data["entities"]]
    assert entity_a.pk not in entity_pks
