import pytest

from django.urls import reverse

from pontoon.base.models import (
    Project,
    ProjectLocale,
    Resource,
    TranslatedResource,
    Translation,
)
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    Repository,
    ResourceFactory,
    TranslationFactory,
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
def locale_b():
    return LocaleFactory(
        code="gs",
        name="Geonosian",
    )


@pytest.fixture
def project_a():
    return ProjectFactory(
        slug="project_a", name="Project A", repositories=[],
    )


@pytest.fixture
def project_b():
    return ProjectFactory(
        slug="project_b", name="Project B"
    )


@pytest.fixture
def resource_a(locale_a, project_a):
    return ResourceFactory(
        project=project_a, path="resource_a.po", format="po"
    )


@pytest.fixture
def entity_a(resource_a):
    return EntityFactory(
        resource=resource_a, string="entity"
    )


@pytest.fixture
def project_locale_a(project_a, locale_a):
    return ProjectLocaleFactory(
        project=project_a,
        locale=locale_a,
    )


@pytest.fixture
def translation_a(locale_a, project_locale_a, entity_a, user_a):
    return TranslationFactory(
        entity=entity_a, locale=locale_a, user=user_a
    )


@pytest.fixture
def approved_translation(locale_a, project_locale_a, entity_a, user_a):
    return TranslationFactory(
        entity=entity_a, locale=locale_a, user=user_a, approved=True
    )


@pytest.fixture
def settings_debug(settings):
    """Make the settings.DEBUG for this test"""
    settings.DEBUG = True


@pytest.yield_fixture
def request_update_translation():
    """
    Call /update/ view to push a translation/suggestion etc.
    """
    def func(client, **args):
        update_params = {
            'translation': 'approved translation',
            'plural_form': '-1',
            'ignore_check': 'true',
        }
        update_params.update(args)

        return client.post(
            '/update/',
            update_params,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
    return func


@pytest.mark.django_db
def test_view_translation_unapprove(approved_translation, member):
    """Check if unapprove view works properly."""
    url = reverse('pontoon.unapprove_translation')
    params = {
        'translation': approved_translation.pk,
        'paths': [],
    }
    response = member.client.post(url, params)
    assert response.status_code == 400
    assert response.content == 'Bad Request: Request must be AJAX'
    response = member.client.post(
        url, params,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 200
    approved_translation.refresh_from_db()
    assert approved_translation.approved is False
    assert approved_translation.unapproved_user == response.wsgi_request.user


@pytest.mark.django_db
def test_view_translate_invalid_locale_project(client, settings_debug):
    """If the locale and project are both invalid, return a 404."""
    response = client.get('/invalid-locale/invalid-project/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_locale(client, resource_a, settings_debug):
    """
    If the project is valid but the locale isn't, redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        '/invalid-locale/%s/%s/'
        % (resource_a.project.slug, resource_a.path)
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_project(
    client,
    resource_a,
    locale_a,
    settings_debug,
):
    """If the project is invalid, redirect home."""
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        '/%s/invalid-project/%s/'
        % (locale_a.code, resource_a.path)
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_invalid_pl(
    client,
    locale_a,
    project_b,
    settings_debug,
):
    """
    If the requested locale is not available for this project,
    redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        '/%s/%s/path/'
        % (locale_a.code, project_b.slug)
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_translate_not_authed_public_project(
    client,
    locale_a,
    settings_debug,
):
    """
    If the user is not authenticated and we're translating project
    ID 1, return a 200.
    """
    # Clear out existing project with ID=1 if necessary.
    Project.objects.filter(id=1).delete()
    project = Project.objects.create(id=1, slug='valid-project')
    ProjectLocale.objects.create(
        project=project, locale=locale_a,
    )
    resource = Resource.objects.create(
        project=project,
        path='foo.lang',
        total_strings=1,
    )
    TranslatedResource.objects.create(
        resource=resource, locale=locale_a,
    )
    response = client.get(
        '/%s/%s/%s/'
        % (locale_a.code, project.slug, resource.path)
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_translate_force_suggestions(
    project_locale_a,
    translation_a,
    locale_a,
    member,
    request_update_translation,
):
    """
    Save/suggest button should always do what the current label says and
    be independent from the user settings in different browser tabs.
    """
    translation_a.locale.translators_group.user_set.add(member.user)
    project_locale_a.translated_strings = 1
    project_locale_a.save()

    response = request_update_translation(
        member.client,
        entity=translation_a.entity.pk,
        original=translation_a.entity.string,
        locale=locale_a.code,
        translation='approved 0',
    )
    assert response.status_code == 200

    assert Translation.objects.last().approved is True

    response = request_update_translation(
        member.client,
        entity=translation_a.entity.pk,
        original=translation_a.entity.string,
        locale=locale_a.code,
        translation='approved translation 0',
        force_suggestions='false',
    )
    assert response.status_code == 200
    assert Translation.objects.last().approved is True

    response = request_update_translation(
        member.client,
        entity=translation_a.entity.pk,
        original=translation_a.entity.string,
        locale=locale_a.code,
        translation='unapproved translation 0',
        force_suggestions='true',
    )
    assert response.status_code == 200
    assert Translation.objects.last().approved is False
