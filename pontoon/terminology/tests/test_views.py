from unittest.mock import patch

import pytest

from pontoon.base.models import Project, Resource
from pontoon.test.factories import (
    EntityFactory,
    ProjectFactory,
    ResourceFactory,
    TermFactory,
)


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
def test_get_terms_from_all_entity_patterns(_, client, locale_a):
    resource = ResourceFactory(format=Resource.Format.FLUENT)
    entity = EntityFactory(
        resource=resource,
        string="""warning =
    .heading = Heads up!
    .message = Some sites build trackers into their content.
""",
    )
    term = TermFactory(text="trackers")
    term.refresh_from_db()

    response = client.get(
        "/terminology/get-terms/",
        {"entity": entity.pk, "locale": locale_a.code},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "text": "trackers",
            "part_of_speech": term.part_of_speech,
            "definition": term.definition,
            "usage": term.usage,
            "translation": None,
            "entity_id": term.entity_id,
            "do_not_translate": False,
        }
    ]


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
def test_get_terms_includes_do_not_translate(_, client, locale_a):
    entity = EntityFactory(string="Download Firefox now.")
    TermFactory(text="Firefox", do_not_translate=True)

    response = client.get(
        "/terminology/get-terms/",
        {"entity": entity.pk, "locale": locale_a.code},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    [payload] = response.json()
    assert payload["text"] == "Firefox"
    assert payload["do_not_translate"] is True
    assert payload["translation"] == "Firefox"
    assert payload["entity_id"] is None


@pytest.mark.django_db
@pytest.mark.parametrize("params", [{}, {"entity": "not-a-number"}])
def test_get_terms_bad_request(client, locale_a, params):
    response = client.get(
        "/terminology/get-terms/",
        {"locale": locale_a.code, **params},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_get_terms_respects_project_visibility(client, admin, locale_a):
    project = ProjectFactory(visibility=Project.Visibility.PRIVATE)
    resource = ResourceFactory(project=project)
    entity = EntityFactory(resource=resource)
    params = {"entity": entity.pk, "locale": locale_a.code}

    response = client.get(
        "/terminology/get-terms/",
        params,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 404

    client.force_login(admin)
    response = client.get(
        "/terminology/get-terms/",
        params,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200
