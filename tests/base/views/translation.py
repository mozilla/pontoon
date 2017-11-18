
import pytest

from django.urls import reverse

from pontoon.base.models import (
    Project, ProjectLocale, Resource, TranslatedResource,
    Translation)


@pytest.mark.django_db
def test_view_translation_unapprove(approved0, member0, locale0):
    """Check if unapprove view works properly."""
    url = reverse('pontoon.unapprove_translation')
    params = {
        'translation': approved0.pk,
        'paths': []}
    response = member0.client.post(url, params)
    assert response.status_code == 400
    assert response.content == 'Bad Request: Request must be AJAX'
    response = member0.client.post(
        url, params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    approved0.refresh_from_db()
    assert approved0.approved is False
    assert approved0.unapproved_user == response.wsgi_request.user


@pytest.mark.django_db
def test_view_translate_invalid_locale_project(client, settings_debug):
    """If the locale and project are both invalid, return a 404."""
    response = client.get('/invalid-locale/invalid-project/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_locale(client, resource0, settings_debug):
    """
    If the project is valid but the locale isn't, redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        '/invalid-locale/%s/%s/'
        % (resource0.project.slug, resource0.path))
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_project(client, resource0,
                                        locale0, settings_debug):
    """If the project is invalid, redirect home."""
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        '/%s/invalid-project/%s/'
        % (locale0.code, resource0.path))
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_pl(client, locale0,
                                   projectX, settings_debug):
    """
    If the requested locale is not available for this project,
    redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        '/%s/%s/path/'
        % (locale0.code, projectX.slug))
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_not_authed_public_project(client, locale0,
                                                  settings_debug):
    """
    If the user is not authenticated and we're translating project
    ID 1, return a 200.
    """
    # Clear out existing project with ID=1 if necessary.
    Project.objects.filter(id=1).delete()
    project = Project.objects.create(id=1, slug='valid-project')
    ProjectLocale.objects.create(
        project=project, locale=locale0)
    resource = Resource.objects.create(
        project=project,
        path='foo.lang',
        total_strings=1)
    TranslatedResource.objects.create(
        resource=resource, locale=locale0)
    response = client.get(
        '/%s/%s/%s/'
        % (locale0.code, project.slug, resource.path))
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_translate_force_suggestions(project_locale0,
                                          translation0, member0):
    """
    Save/suggest button should always do what the current label says and
    be independent from the user settings in different browser tabs.
    """
    translation0.locale.translators_group.user_set.add(member0.user)
    project_locale0.translated_strings = 1
    project_locale0.save()
    update_params = {
        'locale': translation0.locale.code,
        'entity': translation0.entity.pk,
        'translation': 'approved translation',
        'plural_form': '-1',
        'ignore_check': 'true',
        'original': translation0.entity.string}
    response = member0.client.post(
        '/update/',
        update_params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    assert Translation.objects.last().approved is True

    update_params["translation"] = "approved translation2"
    update_params["force_suggestions"] = "false"
    response = member0.client.post(
        '/update/',
        update_params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    assert Translation.objects.last().approved is True

    update_params["translation"] = "unapproved translation"
    update_params["force_suggestions"] = "true"
    response = member0.client.post(
        '/update/',
        update_params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    assert Translation.objects.last().approved is False
