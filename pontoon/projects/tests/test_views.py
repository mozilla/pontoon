from unittest.mock import patch

import pytest

from django.http import HttpResponse
from django.shortcuts import render

from pontoon.base.models import Project
from pontoon.test.factories import TranslatedResourceFactory, TranslationFactory


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
def test_projects_list_stats_exclude_private_projects(
    client, project_a, project_b, locale_a, resource_a, resource_b
):
    """Project list totals exclude private projects for regular users."""
    project_b.visibility = Project.Visibility.PRIVATE
    project_b.save()
    TranslatedResourceFactory.create(
        resource=resource_a, locale=locale_a, total_strings=2, approved_strings=1
    )
    TranslatedResourceFactory.create(
        resource=resource_b, locale=locale_a, total_strings=3, approved_strings=2
    )

    with patch("pontoon.projects.views.render", wraps=render) as mock_render:
        client.get("/projects/")

    stats = mock_render.call_args[0][2]["all_projects_stats"]
    assert stats["total"] == 2
    assert stats["approved"] == 1


@pytest.mark.django_db
def test_projects_list_stats_include_private_projects_for_superuser(
    client_superuser, project_a, project_b, locale_a, resource_a, resource_b
):
    """Project list totals include private projects for superusers."""
    project_b.visibility = Project.Visibility.PRIVATE
    project_b.save()
    TranslatedResourceFactory.create(
        resource=resource_a, locale=locale_a, total_strings=2, approved_strings=1
    )
    TranslatedResourceFactory.create(
        resource=resource_b, locale=locale_a, total_strings=3, approved_strings=2
    )

    with patch("pontoon.projects.views.render", wraps=render) as mock_render:
        client_superuser.get("/projects/")

    stats = mock_render.call_args[0][2]["all_projects_stats"]
    assert stats["total"] == 5
    assert stats["approved"] == 3


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
def test_project_view_private_stats(client_superuser, project_a, locale_a, resource_a):
    """Private project stats are visible to superusers."""
    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()
    TranslatedResourceFactory.create(
        resource=resource_a,
        locale=locale_a,
        total_strings=1,
        approved_strings=1,
    )

    with patch("pontoon.projects.views.render", wraps=render) as mock_render:
        response = client_superuser.get(f"/projects/{project_a.slug}/")

    assert response.status_code == 200
    project_stats = mock_render.call_args[0][2]["project_stats"]
    assert project_stats["total"] > 0
    assert project_stats["approved"] > 0


@pytest.mark.django_db
def test_project_view_private_stats_anonymous(client, project_a, resource_a):
    """Private project stats are hidden from anonymous users."""
    # The project is accessible while public; the 404 below is caused by visibility.
    assert client.get(f"/projects/{project_a.slug}/").status_code == 200

    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()

    assert client.get(f"/projects/{project_a.slug}/").status_code == 404


@pytest.mark.django_db
def test_project_view_private_stats_non_superuser(member, project_a, resource_a):
    """Private project stats are hidden from non-superusers."""
    # The project is accessible while public; the 404 below is caused by visibility.
    assert member.client.get(f"/projects/{project_a.slug}/").status_code == 200

    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()

    assert member.client.get(f"/projects/{project_a.slug}/").status_code == 404


@pytest.mark.django_db
def test_project_view_admin_link(client_superuser, project_a, resource_a):
    """
    Checks that the admin link is only shown for projects with repositories.
    """
    admin_url = f'href="/admin/projects/{project_a.slug}/"'.encode()

    response = client_superuser.get(f"/projects/{project_a.slug}/")
    assert admin_url in response.content

    project_a.repositories.all().delete()
    response = client_superuser.get(f"/projects/{project_a.slug}/")
    assert admin_url not in response.content


@pytest.mark.django_db
def test_project_view_filtered_teams(
    client, locale_a, project_a, project_locale_a, resource_a
):
    """
    Checks if project page is returned properly with filtered teams.
    """
    with patch("pontoon.projects.views.render", wraps=render) as mock_render:
        client.get(f"/projects/{project_a.slug}/?teams={locale_a.code}")
        assert mock_render.call_args[0][2]["project"] == project_a
        assert mock_render.call_args[0][2]["count"] == 1


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


@pytest.mark.django_db
def test_project_teams_latest_activity_locale(client, translation_a):
    """
    Checks if the latest activity tooltip data includes the translation locale.
    """
    locale = translation_a.locale
    locale.direction = "rtl"
    locale.script = "Arab"
    locale.save()

    response = client.get(
        f"/projects/{translation_a.entity.resource.project.slug}/ajax/",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert f'data-translation-locale="{locale.code}"' in content
    assert 'data-translation-direction="rtl"' in content
    assert 'data-translation-script="Arab"' in content
