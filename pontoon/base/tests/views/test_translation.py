from __future__ import absolute_import, unicode_literals

import pytest


@pytest.mark.django_db
def test_view_translate_invalid_locale_project(client, settings_debug):
    """If the locale and project are both invalid, return a 404."""
    response = client.get("/invalid-locale/invalid-project/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_locale(client, resource_a, settings_debug):
    """
    If the project is valid but the locale isn't, redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        "/invalid-locale/%s/%s/" % (resource_a.project.slug, resource_a.path)
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_project(
    client, resource_a, locale_a, settings_debug,
):
    """If the project is invalid, redirect home."""
    # this doesnt seem to redirect as the comment suggests
    response = client.get("/%s/invalid-project/%s/" % (locale_a.code, resource_a.path))
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_pl(
    client, locale_a, project_b, settings_debug,
):
    """
    If the requested locale is not available for this project,
    redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get("/%s/%s/path/" % (locale_a.code, project_b.slug))
    assert response.status_code == 404
