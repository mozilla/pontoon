import factory
import pytest
from mock import patch

from django.contrib.auth import get_user_model
from django.shortcuts import render

from pontoon.base.models import (
    Group,
    Locale,
    Project,
    ProjectLocale,
    Resource,
)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()


@pytest.fixture
def fakeuser():
    return UserFactory(
        username="fakeuser",
        email="fakeuser@example.org"
    )


@pytest.fixture
def member(client, fakeuser):
    """Provides a `LoggedInMember` with the attributes `user` and `client`
    the `client` is authenticated
    """

    class LoggedInMember(object):

        def __init__(self, user, client):
            client.force_login(user)
            self.client = client
            self.user = user

    return LoggedInMember(fakeuser, client)


@pytest.fixture
def locale():
    translators_group = Group.objects.create(
        name='Klingon translators',
    )
    managers_group = Group.objects.create(
        name='Klingon managers',
    )
    return Locale.objects.create(
        code="kg",
        name="Klingon",
        translators_group=translators_group,
        managers_group=managers_group,
    )


@pytest.fixture
def project():
    return Project.objects.create(
        slug="project", name="Project"
    )


@pytest.fixture
def project_locale(project, locale):
    pl = ProjectLocale.objects.create(project=project, locale=locale)
    # ProjectLocale doesn't work without at least one resource.
    Resource.objects.create(
        project=project,
        path='foo.lang',
        total_strings=1
    )
    return pl


@pytest.fixture
def translators():
    translators = [
        UserFactory(
            username='Translator %s' % x,
            email='translator%s@example.org' % x,
        )
        for x in range(3)
    ]
    sorted_translators = sorted(
        translators,
        key=lambda u: u.email
    )
    return sorted_translators


@pytest.fixture
def managers():
    managers = [
        UserFactory(
            username='Manager %s' % x,
            email='manager%s@example.org' % x,
        )
        for x in range(3)
    ]
    sorted_managers = sorted(
        managers,
        key=lambda u: u.email
    )
    return sorted_managers


@pytest.mark.django_db
@patch('pontoon.teams.views.render', wraps=render)
def test_ajax_permissions_locale_translators_managers_order(
        render_mock,
        admin_client,
        locale,
        translators,
        managers,
):
    """
    Translators and managers of a locale should be sorted by email in
    "Permissions" tab.
    """
    locale.translators_group.user_set.add(*translators)
    locale.managers_group.user_set.add(*managers)

    admin_client.get('/%s/ajax/permissions/' % locale.code)
    response_context = render_mock.call_args[0][2]

    assert list(response_context['translators']) == translators
    assert list(response_context['managers']) == managers


@pytest.mark.django_db
@patch('pontoon.teams.views.render', wraps=render)
def test_ajax_permissions_project_locale_translators_order(
    render_mock,
    admin_client,
    locale,
    project_locale,
    translators,
):
    """
    Translators and managers of a locale should be sorted by email in
    "Permissions" tab.
    """
    project_locale.translators_group.user_set.add(*translators)

    admin_client.get('/%s/ajax/permissions/' % locale.code)
    response_context = render_mock.call_args[0][2]
    locale_projects = response_context['locale_projects']

    # Check project_locale id in the permissions form
    assert locale_projects[0][0] == project_locale.pk

    # Check project_locale translators
    translators_list = [
        {
            'id': u.id,
            'email': u.email,
            'first_name': u.first_name,
        }
        for u in translators
    ]
    assert locale_projects[0][4] == translators_list


@pytest.mark.django_db
def test_users_permissions_for_ajax_permissions_view(
    client,
    locale,
    member,
):
    """
    Check if anonymous users and users without permissions can't access
    Permissions Tab.
    """

    response = client.get('/{locale}/ajax/permissions/'.format(
        locale=locale.code
    ))
    assert response.status_code == 403
    assert '<title>Forbidden page</title>' in response.content

    # Check if users without permissions for the locale can get this tab.
    response = member.client.get('/{locale}/ajax/permissions/'.format(
        locale=locale.code
    ))
    assert response.status_code == 403
    assert '<title>Forbidden page</title>' in response.content

    locale.managers_group.user_set.add(member.user)

    # Bump up permissions for user0 and check if the view is accessible.
    response = member.client.get('/{locale}/ajax/permissions/'.format(
        locale=locale.code
    ))
    assert response.status_code == 200
    assert '<title>Forbidden page</title>' not in response.content

    # Remove permissions for user0 and check if the view is not accessible.
    locale.managers_group.user_set.clear()

    response = member.client.get('/{locale}/ajax/permissions/'.format(
        locale=locale.code
    ))
    assert response.status_code == 403
    assert '<title>Forbidden page</title>' in response.content

    # All unauthorized attempts to POST data should be blocked
    response = member.client.post(
        '/{locale}/ajax/permissions/'.format(
            locale=locale.code
        ),
        data={'smth': 'smth'}
    )
    assert response.status_code == 403
    assert '<title>Forbidden page</title>' in response.content

    response = client.post(
        '/{locale}/ajax/permissions/'.format(
            locale=locale.code
        ),
        data={'smth': 'smth'}
    )
    assert response.status_code == 403
    assert '<title>Forbidden page</title>' in response.content
