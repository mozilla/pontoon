from unittest.mock import patch

import pytest
from django.http import HttpResponse
from django.shortcuts import render

from pontoon.base.tests import (
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
)


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
def test_project_view(client):
    """
    Checks if project page is returned properly.
    """
    project = ProjectFactory.create(visibility="public")
    ResourceFactory.create(project=project)

    with patch("pontoon.projects.views.render", wraps=render) as mock_render:
        client.get("/projects/{}/".format(project.slug))
        assert mock_render.call_args[0][2]["project"] == project


@pytest.mark.django_db
def test_project_top_contributors(client):
    """
    Tests if view returns top contributors specific for given project.
    """
    first_project = ProjectFactory.create(visibility="public")
    ResourceFactory.create(project=first_project)
    first_project_contributor = TranslationFactory.create(
        entity__resource__project=first_project
    ).user

    second_project = ProjectFactory.create(visibility="public")
    ResourceFactory.create(project=second_project)
    second_project_contributor = TranslationFactory.create(
        entity__resource__project=second_project
    ).user

    with patch(
        "pontoon.projects.views.ProjectContributorsView.render_to_response",
        return_value=HttpResponse(""),
    ) as mock_render:
        client.get(
            "/projects/{}/ajax/contributors/".format(first_project.slug),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert mock_render.call_args[0][0]["project"] == first_project
        assert list(mock_render.call_args[0][0]["contributors"]) == [
            first_project_contributor
        ]

        client.get(
            "/projects/{}/ajax/contributors/".format(second_project.slug),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert mock_render.call_args[0][0]["project"] == second_project
        assert list(mock_render.call_args[0][0]["contributors"]) == [
            second_project_contributor
        ]
