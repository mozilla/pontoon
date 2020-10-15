import pytest
from mock import patch

from django.http import HttpResponse
from django.shortcuts import render

from pontoon.test.factories import UserFactory


def _get_sorted_users():
    return sorted(UserFactory.create_batch(size=3), key=lambda u: u.email)


@pytest.fixture
def translators():
    return _get_sorted_users()


@pytest.fixture
def managers():
    return _get_sorted_users()


@pytest.mark.django_db
def test_missing_locale(client):
    """
    Tests if the backend is returning an error on the missing locale.
    """
    response = client.get("/missing-locale/")

    assert response.status_code == 404
    assert response.resolver_match.view_name == "pontoon.teams.team"


@pytest.mark.django_db
@patch("pontoon.teams.views.render", wraps=render)
def test_locale_view(mock_render, translation_a, client):
    """
    Check if the locale view finds the right locale and passes it to the template.
    """
    client.get("/{locale}/".format(locale=translation_a.locale.code))

    assert mock_render.call_args[0][2]["locale"] == translation_a.locale


@pytest.mark.django_db
def test_contributors_of_missing_locale(client):
    """
    Tests if the contributors view is returning an error on the missing locale.
    """
    response = client.get("/missing-locale/contributors/")

    assert response.status_code == 404
    assert response.resolver_match.view_name == "pontoon.teams.contributors"


@pytest.mark.django_db
@patch("pontoon.teams.views.render", wraps=render)
def test_ajax_permissions_locale_translators_managers_order(
    render_mock, admin_client, locale_a, translators, managers,
):
    """
    Translators and managers of a locale should be sorted by email in
    "Permissions" tab.
    """
    locale_a.translators_group.user_set.add(*translators)
    locale_a.managers_group.user_set.add(*managers)

    admin_client.get("/%s/ajax/permissions/" % locale_a.code)
    response_context = render_mock.call_args[0][2]

    assert list(response_context["translators"]) == translators
    assert list(response_context["managers"]) == managers


@pytest.mark.django_db
@patch("pontoon.teams.views.render", wraps=render)
def test_ajax_permissions_project_locale_translators_order(
    render_mock,
    admin_client,
    locale_a,
    project_locale_a,
    resource_a,  # required for project_locale_a to work
    translators,
):
    """
    Translators and managers of a locale should be sorted by email in
    "Permissions" tab.
    """
    project_locale_a.translators_group.user_set.add(*translators)

    admin_client.get("/%s/ajax/permissions/" % locale_a.code)
    response_context = render_mock.call_args[0][2]
    locale_projects = response_context["locale_projects"]

    # Check project_locale id in the permissions form
    assert locale_projects[0][0] == project_locale_a.pk

    # Check project_locale translators
    translators_list = [
        {"id": u.id, "email": u.email, "first_name": u.first_name} for u in translators
    ]
    assert locale_projects[0][4] == translators_list


@pytest.mark.django_db
def test_users_permissions_for_ajax_permissions_view(
    client, locale_a, member,
):
    """
    Check if anonymous users and users without permissions can't access
    Permissions Tab.
    """

    response = client.get("/{locale}/ajax/permissions/".format(locale=locale_a.code))
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content

    # Check if users without permissions for the locale can get this tab.
    response = member.client.get(
        "/{locale}/ajax/permissions/".format(locale=locale_a.code)
    )
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content

    locale_a.managers_group.user_set.add(member.user)

    # Bump up permissions for user0 and check if the view is accessible.
    response = member.client.get(
        "/{locale}/ajax/permissions/".format(locale=locale_a.code)
    )
    assert response.status_code == 200
    assert b"<title>Forbidden page</title>" not in response.content

    # Remove permissions for user0 and check if the view is not accessible.
    locale_a.managers_group.user_set.clear()

    response = member.client.get(
        "/{locale}/ajax/permissions/".format(locale=locale_a.code)
    )
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content

    # All unauthorized attempts to POST data should be blocked
    response = member.client.post(
        "/{locale}/ajax/permissions/".format(locale=locale_a.code),
        data={"smth": "smth"},
    )
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content

    response = client.post(
        "/{locale}/ajax/permissions/".format(locale=locale_a.code),
        data={"smth": "smth"},
    )
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content


@pytest.mark.django_db
@patch(
    "pontoon.teams.views.LocaleContributorsView.render_to_response",
    return_value=HttpResponse(""),
)
def test_locale_top_contributors(mock_render, client, translation_a, locale_b):
    """
    Tests if the view returns top contributors specific for given locale.
    """
    client.get(
        "/{locale}/ajax/contributors/".format(locale=translation_a.locale.code),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    response_context = mock_render.call_args[0][0]
    assert response_context["locale"] == translation_a.locale
    assert list(response_context["contributors"]) == [translation_a.user]

    client.get(
        "/{locale}/ajax/contributors/".format(locale=locale_b.code),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    response_context = mock_render.call_args[0][0]
    assert response_context["locale"] == locale_b
    assert list(response_context["contributors"]) == []
