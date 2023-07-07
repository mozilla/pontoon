import pytest

from django.contrib.auth import get_user_model

from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from pontoon.base.models import Project
from pontoon.base.utils import (
    aware_datetime,
    extension_in,
    get_m2m_changes,
    get_object_or_none,
    latest_datetime,
    get_search_phrases,
    is_email,
)

from pontoon.test.factories import (
    ProjectFactory,
    ResourceFactory,
    LocaleFactory,
    ProjectSlugHistoryFactory,
    ProjectLocaleFactory,
)


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
    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_b.pk, user_c.pk]),
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
    ) == ([user_a], [user_c])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_a.pk, user_b.pk]),
        get_user_model().objects.filter(pk__in=[user_c.pk]),
    ) == ([user_c], [user_a, user_b])

    assert get_m2m_changes(
        get_user_model().objects.filter(pk__in=[user_b.pk]),
        get_user_model().objects.filter(pk__in=[user_c.pk, user_a.pk]),
    ) == ([user_a, user_c], [user_b])


def test_util_base_extension_in():
    assert extension_in("filename.txt", ["bat", "txt"])
    assert extension_in("filename.biff", ["biff"])
    assert extension_in("filename.tar.gz", ["gz"])

    assert not extension_in("filename.txt", ["png", "jpg"])
    assert not extension_in(".dotfile", ["bat", "txt"])

    # Unintuitive, but that's how splitext works.
    assert not extension_in("filename.tar.gz", ["tar.gz"])


@pytest.mark.django_db
def test_util_base_get_object_or_none(project_a):
    assert get_object_or_none(Project, slug="does-not-exist") is None
    assert get_object_or_none(Project, slug=project_a.slug) == project_a


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
