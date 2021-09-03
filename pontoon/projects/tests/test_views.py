from unittest.mock import patch

import pytest
from django.http import HttpResponse
from django.shortcuts import render

from pontoon.base.tests import TranslationFactory


@pytest.mark.no_cover
@pytest.mark.django_db
def test_projects_list(client, project_a, resource_a):
    """
    Checks if list of projects is properly rendered.
    """
    response = client.get("/projects/")
    assert response.status_code == 200
    assert response.resolver_match.view_name == "pontoon.projects"


@pytest.mark.django_db
def test_project_doesnt_exist(client):
    """
    Checks if view is returning error when project slug is invalid.
    """
    response = client.get("/projects/project_doesnt_exist/")
    assert response.status_code == 404
    response = client.get("/projects/project_doesnt_exist/contributors/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_project_view(client, project_a, resource_a):
    """
    Checks if project page is returned properly.
    """
    with patch("pontoon.projects.views.render", wraps=render) as mock_render:
        client.get(f"/projects/{project_a.slug}/")
        assert mock_render.call_args[0][2]["project"] == project_a


@pytest.mark.django_db
def test_project_top_contributors(client, project_a, project_b):
    """
    Tests if view returns top contributors specific for given project.
    """
    project_a_contributor = TranslationFactory.create(
        entity__resource__project=project_a
    ).user

    project_b_contributor = TranslationFactory.create(
        entity__resource__project=project_b
    ).user

    with patch(
        "pontoon.projects.views.ProjectContributorsView.render_to_response",
        return_value=HttpResponse(""),
    ) as mock_render:
        client.get(
            f"/projects/{project_a.slug}/ajax/contributors/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert mock_render.call_args[0][0]["project"] == project_a
        assert list(mock_render.call_args[0][0]["contributors"]) == [
            project_a_contributor
        ]

        client.get(
            f"/projects/{project_b.slug}/ajax/contributors/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert mock_render.call_args[0][0]["project"] == project_b
        assert list(mock_render.call_args[0][0]["contributors"]) == [
            project_b_contributor
        ]
