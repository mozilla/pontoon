import json

import pytest

from pontoon.base.models import TranslatedResource
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    TranslationFactory,
)


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


@pytest.mark.django_db
def test_entities_not_matching_string_reports_location(member, entity_a, locale_a):
    """
    When the requested `string` exists and is viewable but doesn't match the
    active filters, the response reports where it actually lives so the frontend
    can offer to navigate there. Regression test for
    https://github.com/mozilla/pontoon/issues/2921
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
    assert data["requested_entity"] == {
        "pk": entity_a.pk,
        "project": entity_a.resource.project.slug,
        "project_name": entity_a.resource.project.name,
        "resource": entity_a.resource.path,
        "filters": ["missing"],
    }

    response = member.client.post(
        "/get-entities/",
        {
            "project": entity_a.resource.project.slug,
            "locale": locale_a.code,
            "paths[]": [entity_a.resource.path],
            "entity": entity_a.pk,
            "page": 1,
            "limit": 50,
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    data = json.loads(response.content)
    assert entity_a.pk in [e["pk"] for e in data["entities"]]
    assert "requested_entity" not in data
