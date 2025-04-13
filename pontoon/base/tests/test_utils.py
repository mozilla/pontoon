import pytest

from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from pontoon.base.utils import (
    aware_datetime,
    get_m2m_changes,
    get_search_phrases,
    is_email,
    latest_datetime,
)
from pontoon.test.factories import (
    LocaleCodeHistoryFactory,
    LocaleFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    ProjectSlugHistoryFactory,
    ResourceFactory,
)


@pytest.fixture
def locale_a():
    """
    Fixture that sets up and returns a Locale.
    """
    return LocaleFactory.create(code="locale-a", name="Locale A")


def create_code_history_and_change_code(locale, new_code):
    """
    Helper function to simulate changing a locale's code.
    It records the locale's current code in the history, then updates the locale's code.
    """
    LocaleCodeHistoryFactory.create(locale=locale, old_code=locale.code)
    locale.code = new_code
    locale.save()
    locale.refresh_from_db()
    return locale


@pytest.mark.django_db
def test_settings_view_with_changed_locale(client, user_a, locale_a):
    """
    Test the settings view when the user's custom homepage locale has changed.
    """
    # Set up the user's profile with an old locale code
    profile = user_a.profile
    old_code = locale_a.code
    new_code = "locale-a-new-1"
    profile.custom_homepage = old_code
    profile.save()

    # Simulate the locale code change
    locale_a = create_code_history_and_change_code(locale_a, new_code)

    client.force_login(user_a)
    response = client.get(reverse("pontoon.contributors.settings"))

    # Check if the view correctly handles the changed locale
    assert response.status_code == 200


@pytest.mark.django_db
def test_handle_old_code_redirect_no_loop(client, locale_a, project_a):
    """
    Test that there is no redirect loop when a locale's code is renamed and then renamed back to the original.
    """
    # Rename locale code and then rename it back
    create_code_history_and_change_code(locale_a, "code-b")
    create_code_history_and_change_code(locale_a, "code-c")
    create_code_history_and_change_code(locale_a, "code-a")

    # Request the view with the original locale code
    response = client.get(
        reverse(
            "pontoon.localizations.localization",
            kwargs={"code": "code-a", "slug": project_a.slug},
        )
    )

    # Assert that the response is not a redirect (status code is not 302)
    assert response.status_code != 302


@pytest.mark.django_db
def test_localization_view_with_changed_locale(client, locale_a, project_a):
    """
    Test the localization view with a changed locale code.
    """
    old_code = locale_a.code
    new_code = "locale-a-new-2"
    locale_a = create_code_history_and_change_code(locale_a, new_code)

    response = client.get(
        reverse(
            "pontoon.localizations.localization",
            kwargs={"code": old_code, "slug": project_a.slug},
        )
    )

    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse(
        "pontoon.localizations.localization",
        kwargs={"code": new_code, "slug": project_a.slug},
    )


@pytest.mark.django_db
def test_handle_no_code_redirect_localization(client, project_a):
    """
    Test to ensure that an attempt to access a localization view without a code raises a NoReverseMatch exception.
    """
    with pytest.raises(NoReverseMatch):
        client.get(
            reverse(
                "pontoon.localizations.localization",
                kwargs={"slug": project_a.slug},
            )
        )


@pytest.mark.django_db
def test_handle_nonexistent_code_redirect_localization(client, project_a):
    """
    Test to ensure that an attempt to access a localization view with a non-existent code returns a 404 error.
    """
    code = "nonexistent-code"

    response = client.get(
        reverse(
            "pontoon.localizations.localization",
            kwargs={"code": code, "slug": project_a.slug},
        )
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_translate_view_with_changed_locale(client, locale_a, project_a, resource_a):
    """
    Test the translate view with a changed locale code.
    """
    old_code = locale_a.code
    new_code = "locale-a-new-3"
    locale_a = create_code_history_and_change_code(locale_a, new_code)

    response = client.get(
        reverse(
            "pontoon.translate",
            kwargs={
                "locale": old_code,
                "project": project_a.slug,
                "resource": resource_a.path,
            },
        )
    )

    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse(
        "pontoon.translate",
        kwargs={
            "locale": new_code,
            "project": project_a.slug,
            "resource": resource_a.path,
        },
    )


@pytest.mark.django_db
def test_handle_no_code_redirect_translate(client, project_a, resource_a):
    """
    Test to ensure that an attempt to access the translate view without a locale code raises a NoReverseMatch exception.
    """
    with pytest.raises(NoReverseMatch):
        client.get(
            reverse(
                "pontoon.translate",
                kwargs={"project": project_a.slug, "resource": resource_a.path},
            )
        )


@pytest.mark.django_db
def test_handle_nonexistent_code_redirect_translate(client, project_a, resource_a):
    """
    Test to ensure that an attempt to access the translate view with a non-existent locale code returns a 404 error.
    """
    code = "nonexistent-code"

    response = client.get(
        reverse(
            "pontoon.translate",
            kwargs={
                "locale": code,
                "project": project_a.slug,
                "resource": resource_a.path,
            },
        )
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_team_view_with_changed_locale(client, locale_a):
    """
    Test the team view with a changed locale code.
    """
    old_code = locale_a.code
    new_code = "locale-a-new-4"
    locale_a = create_code_history_and_change_code(locale_a, new_code)

    response = client.get(reverse("pontoon.teams.team", kwargs={"locale": old_code}))

    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("pontoon.teams.team", kwargs={"locale": new_code})


@pytest.mark.django_db
def test_handle_no_code_redirect_team(client):
    """
    Test to ensure that an attempt to access the team view without a locale code raises a NoReverseMatch exception.
    """
    with pytest.raises(NoReverseMatch):
        client.get(
            reverse(
                "pontoon.teams.team",
                kwargs={},
            )
        )


@pytest.mark.django_db
def test_handle_nonexistent_code_redirect_team(client):
    """
    Test to ensure that an attempt to access the team view with a non-existent locale code returns a 404 error.
    """
    code = "nonexistent-code"

    response = client.get(
        reverse(
            "pontoon.teams.team",
            kwargs={"locale": code},
        )
    )

    assert response.status_code == 404


@pytest.fixture
def project_d():
    """
    Fixture that sets up and returns a Project with associated Locale and Resource.
    """
    locale = LocaleFactory.create()
    project = ProjectFactory.create(
        name="Project D", slug="project-d", disabled=False, system_project=False
    )
    ResourceFactory.create(project=project, path="resource_d.po", format="po")
    ProjectLocaleFactory.create(project=project, locale=locale)
    return project


def create_slug_history_and_change_slug(project, new_slug):
    """
    This function is a helper for tests that need to simulate changing a project's slug.
    It records the project's current slug in the history, then updates the project's slug
    to a new value.
    """
    # Record the old slug in the history
    ProjectSlugHistoryFactory.create(project=project, old_slug=project.slug)

    # Change the slug of the project to the new_slug
    project.slug = new_slug
    project.save()
    project.refresh_from_db()

    return project


@pytest.mark.django_db
def test_project_view_redirects_old_slug(client, project_d):
    """
    Test to ensure that accessing a project view with an old slug redirects to the new slug URL.
    """
    old_slug = project_d.slug
    new_slug = "project-d-new-1"
    project_d = create_slug_history_and_change_slug(project_d, new_slug)

    # First access the URL with the new slug and ensure it's working
    response = client.get(
        reverse("pontoon.projects.project", kwargs={"slug": new_slug})
    )
    assert response.status_code == 200

    # Now access the URL with the old slug
    response = client.get(
        reverse("pontoon.projects.project", kwargs={"slug": old_slug})
    )
    # The old slug should cause a redirect to the new slug URL
    assert response.status_code == 302
    assert response.url == reverse(
        "pontoon.projects.project", kwargs={"slug": new_slug}
    )


@pytest.mark.django_db
def test_handle_old_slug_redirect_no_loop(client, project_d):
    """
    Test that there is no redirect loop when a project's slug is renamed from 'cc' to 'dd' and then back to 'cc'.
    """
    # Rename project from 'cc' to 'dd' and then back to 'cc'
    create_slug_history_and_change_slug(project_d, "cc")
    create_slug_history_and_change_slug(project_d, "dd")
    create_slug_history_and_change_slug(project_d, "cc")

    # Request the project detail view with slug 'cc'
    response = client.get(reverse("pontoon.projects.project", kwargs={"slug": "cc"}))

    # Assert that the response is not a redirect (status code is not 302)
    assert response.status_code != 302


@pytest.mark.django_db
def test_handle_old_slug_redirect_no_redirect_to_different_project(client, project_d):
    """
    Test that a request for a slug that was changed and then reused by a different project does not redirect to the original project.
    """
    # Rename project from 'ee' to 'ff'
    create_slug_history_and_change_slug(project_d, "ee")
    create_slug_history_and_change_slug(project_d, "ff")

    # Create a new project with slug 'ee'
    project = ProjectFactory.create(
        name="Project E", slug="ee", disabled=False, system_project=False
    )
    ResourceFactory.create(project=project, path="resource_e.po", format="po")

    # Request the project detail view with slug 'ee'
    response = client.get(reverse("pontoon.projects.project", kwargs={"slug": "ee"}))

    # Assert that the response is successful (status code is 200)
    assert response.status_code == 200


@pytest.mark.django_db
def test_handle_no_slug_redirect_project(client):
    """
    Test to ensure that an attempt to access a project view without a slug raises a NoReverseMatch exception.
    """
    with pytest.raises(NoReverseMatch):
        # Try to access the URL without a slug
        client.get(reverse("pontoon.projects.project", kwargs={}))


@pytest.mark.django_db
def test_handle_nonexistent_slug_redirect_project(client):
    """
    Test to ensure that an attempt to access a project view with a non-existent slug returns a 404 error.
    """
    slug = "nonexistent-slug"

    response = client.get(reverse("pontoon.projects.project", kwargs={"slug": slug}))

    # The expectation here is that the server should return a 404 error
    assert response.status_code == 404


@pytest.mark.django_db
def test_translation_view_redirects_old_slug(client, project_d):
    """
    Test to ensure that accessing a translation view with an old slug redirects to the new slug URL.
    """
    # Add resource to project
    resource_path = "resource_d.po"

    old_slug = project_d.slug
    new_slug = "project-d-new-2"
    locale = project_d.locales.first().code
    project_d = create_slug_history_and_change_slug(project_d, new_slug)

    # First access the URL with the new slug and ensure it's working
    response = client.get(
        reverse(
            "pontoon.translate",
            kwargs={"project": new_slug, "locale": locale, "resource": resource_path},
        )
    )
    assert response.status_code == 200

    # Now access the URL with the old slug
    response = client.get(
        reverse(
            "pontoon.translate",
            kwargs={"project": old_slug, "locale": locale, "resource": resource_path},
        )
    )
    # The old slug should cause a redirect to the new slug URL
    assert response.status_code == 302
    assert response.url == reverse(
        "pontoon.translate",
        kwargs={"project": new_slug, "locale": locale, "resource": resource_path},
    )


@pytest.mark.django_db
def test_handle_no_slug_redirect_translate(client, project_d):
    """
    Test to ensure that an attempt to access a translate view without a slug raises a NoReverseMatch exception.
    """
    locale = project_d.locales.first().code
    resource_path = "resource_d.po"

    with pytest.raises(NoReverseMatch):
        client.get(
            reverse(
                "pontoon.translate",
                kwargs={"locale": locale, "resource": resource_path},
            )
        )


@pytest.mark.django_db
def test_handle_nonexistent_slug_redirect_translate(client, project_d):
    """
    Test to ensure that an attempt to access a translate view with a non-existent slug returns a 404 error.
    """
    locale = project_d.locales.first().code
    resource_path = "resource_d.po"
    slug = "nonexistent-slug"

    response = client.get(
        reverse(
            "pontoon.translate",
            kwargs={"project": slug, "locale": locale, "resource": resource_path},
        )
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_localization_view_redirects_old_slug(client, project_d):
    """
    Test to ensure that accessing a localization view with an old slug redirects to the new slug URL.
    """
    old_slug = project_d.slug
    new_slug = "project-d-new-3"
    locale = project_d.locales.first().code
    project_d = create_slug_history_and_change_slug(project_d, new_slug)

    # First access the URL with the new slug and ensure it's working
    response = client.get(
        reverse(
            "pontoon.localizations.localization",
            kwargs={"slug": new_slug, "code": locale},
        )
    )
    assert response.status_code == 200

    # Now access the URL with the old slug
    response = client.get(
        reverse(
            "pontoon.localizations.localization",
            kwargs={"slug": old_slug, "code": locale},
        )
    )
    # The old slug should cause a redirect to the new slug URL
    assert response.status_code == 302
    assert response.url == reverse(
        "pontoon.localizations.localization",
        kwargs={"slug": new_slug, "code": locale},
    )


@pytest.mark.django_db
def test_handle_no_slug_redirect_localization(client, project_d):
    """
    Test to ensure that an attempt to access a localization view without a slug raises a NoReverseMatch exception.
    """
    locale = project_d.locales.first().code

    with pytest.raises(NoReverseMatch):
        client.get(
            reverse(
                "pontoon.localizations.localization",
                kwargs={"code": locale},
            )
        )


@pytest.mark.django_db
def test_handle_nonexistent_slug_redirect_localization(client, project_d):
    """
    Test to ensure that an attempt to access a localization view with a non-existent slug returns a 404 error.
    """
    locale = project_d.locales.first().code
    slug = "nonexistent-slug"

    response = client.get(
        reverse(
            "pontoon.localizations.localization",
            kwargs={"slug": slug, "code": locale},
        )
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_get_m2m_changes_no_change(user_a):
    assert get_m2m_changes(
        get_user_model().objects.none(), get_user_model().objects.none()
    ) == ([], [])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user_a.pk),
        get_user_model().objects.filter(pk=user_a.pk),
    ) == ([], [])


@pytest.mark.django_db
def test_get_m2m_added(user_a, user_b):
    assert get_m2m_changes(
        get_user_model().objects.none(), get_user_model().objects.filter(pk=user_b.pk)
    ) == ([user_b], [])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user_a.pk),
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
    ) == ([user_b], [])


@pytest.mark.django_db
def test_get_m2m_removed(user_a, user_b):
    assert get_m2m_changes(
        get_user_model().objects.filter(pk=user_b.pk),
        get_user_model().objects.none(),
    ) == ([], [user_b])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
        get_user_model().objects.filter(pk=user_a.pk),
    ) == ([], [user_b])


@pytest.mark.django_db
def test_get_m2m_mixed(user_a, user_b, user_c):
    changes = get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_b.pk, user_c.pk]),
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
    )
    assert [user_a] == changes[0]
    assert [user_c] == changes[1]

    changes = get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
        get_user_model().objects.filter(pk__in=[user_c.pk]),
    )
    assert [user_c] == changes[0]
    assert user_a in changes[1]
    assert user_b in changes[1]

    changes = get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_b.pk]),
        get_user_model().objects.filter(pk__in=[user_c.pk, user_a.pk]),
    )
    assert user_a in changes[0]
    assert user_c in changes[0]
    assert [user_b] == changes[1]


def test_util_base_latest_datetime():
    larger = aware_datetime(2015, 1, 1)
    smaller = aware_datetime(2014, 1, 1)
    assert latest_datetime([None, None, None]) is None
    assert latest_datetime([None, larger]) == larger
    assert latest_datetime([None, smaller, larger]) == larger


@pytest.mark.parametrize(
    "search_query,expected_results",
    (
        ("", []),
        ("lorem ipsum dolor", ["lorem", "ipsum", "dolor"]),
        ('"lorem ipsum dolor"', ["lorem ipsum dolor"]),
        ('"lorem ipsum" dolor', ["lorem ipsum", "dolor"]),
        ('"lorem ipsum" "dolor dolor"', ["lorem ipsum", "dolor dolor"]),
    ),
)
def test_get_search_phrases(search_query, expected_results):
    assert get_search_phrases(search_query) == expected_results


def test_is_email():
    assert is_email("jane@doe.com") is True
    assert is_email("john@doe") is False
