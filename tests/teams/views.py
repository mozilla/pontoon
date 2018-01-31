import pytest

from django.shortcuts import render
from mock import patch


@pytest.yield_fixture
def sorted_locale0_translators(
    locale0,
    user_factory
):
    """
    Assign (& yield) sorted translators to locale0
    """
    sorted_translators = sorted(
        user_factory(batch=3),
        key=lambda u: u.email
    )

    locale0.translators_group.user_set.add(*sorted_translators)
    yield sorted_translators


@pytest.yield_fixture
def sorted_locale0_managers(
    locale0,
    user_factory
):
    """
    Assign (& yield) sorted managers to locale0
    """
    sorted_managers = sorted(
        user_factory(batch=3),
        key=lambda u: u.email
    )
    locale0.managers_group.user_set.add(*sorted_managers)

    yield sorted_managers


@pytest.yield_fixture
def sorted_project_locale0_translators(
        project_locale0,
        user_factory
):
    """
    Assign (& yield) sorted managers to project_locale0.
    Users are passed as a list of dictionaries to permissions template.
    """
    translators = [
        {
            'id': u.pk,
            'first_name': u.first_name,
            'email': u.email
        }
        for u in user_factory(batch=3)
    ]
    
    sorted_translators = sorted(
        translators,
        key=lambda u: u['email']
    )
    project_locale0.translators_group.user_set.add(*[u['id'] for u in translators])

    yield sorted_translators


@pytest.mark.django_db
@patch('pontoon.teams.views.render', wraps=render)
def test_ajax_permissions_locale_translators_managers_order(
        render_mock,
        admin_client,
        locale0,
        sorted_locale0_translators,
        sorted_locale0_managers,
):
    """
    Translators and managers of a locale should be sorted by email in "Permissions" tab.
    """
    admin_client.get('/{locale}/ajax/permissions/'.format(
        locale=locale0.code
    ))
    response_context = render_mock.call_args[0][2]

    assert list(response_context['translators']) == sorted_locale0_translators
    assert list(response_context['managers']) == sorted_locale0_managers


@pytest.mark.django_db
@patch('pontoon.teams.views.render', wraps=render)
def test_ajax_permissions_project_locale_translators_order(
        render_mock,
        admin_client,
        locale0,
        project_locale0,
        sorted_project_locale0_translators,
):
    """
    Translators and managers of a locale should be sorted by email in "Permissions" tab.
    """
    admin_client.get('/{locale}/ajax/permissions/'.format(
        locale=locale0.code
    ))
    response_context = render_mock.call_args[0][2]
    locale_projects = response_context['locale_projects']

    # Check project_locale0 id in the permissions form
    assert locale_projects[0][0] == project_locale0.pk

    # Check project_locale0 translators
    assert locale_projects[0][4] == sorted_project_locale0_translators
