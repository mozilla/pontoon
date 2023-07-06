import pytest

from django.contrib.auth import get_user_model

from django.urls import reverse

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
    UserFactory,
    LocaleFactory,
    ProjectSlugHistoryFactory,
    EntityFactory,
    ProjectLocaleFactory,
)


@pytest.fixture
def project_c():
    project = ProjectFactory.create(name="Project C", slug="project-c", disabled=False)
    ResourceFactory.create(project=project, path="resource_c.po", format="po")
    return project


@pytest.mark.django_db
def test_handle_old_slug_redirect(client, project_c):
    old_slug = project_c.slug
    new_slug = "project-c-new"

    # Change the slug of project_c to the new_slug
    project_c.slug = new_slug
    project_c.save()
    project_c.refresh_from_db()

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


@pytest.fixture
def project_d():
    locale = LocaleFactory.create()
    project = ProjectFactory.create(
        name="Project D", slug="project-d", disabled=False, system_project=False
    )
    ResourceFactory.create(project=project, path="resource_d.po", format="po")
    ProjectLocaleFactory.create(
        project=project, locale=locale
    )  # Pass the locale to the ProjectLocaleFactory.
    return project


@pytest.fixture
def entity_d(project_d):
    return EntityFactory.create(resource=project_d.resources.first(), string="Entity D")


@pytest.mark.django_db
def test_handle_old_slug_redirect_translate(client, project_d, entity_d):
    # Add resource to project
    resource_path = "resource_d.po"

    old_slug = project_d.slug
    new_slug = "project-d-new"

    # Record the old slug in the history
    ProjectSlugHistoryFactory.create(project=project_d, old_slug=old_slug)

    # Change the slug of project_a to the new_slug
    project_d.slug = new_slug
    project_d.save()
    project_d.refresh_from_db()

    # The user is needed for the request
    user = UserFactory.create(is_superuser=True)
    client.force_login(user)

    # First access the URL with the new slug and ensure it's working
    response = client.get(
        reverse(
            "pontoon.translate",
            kwargs={"project": new_slug, "locale": "en", "resource": resource_path},
        )
    )
    assert response.status_code == 200

    # Now access the URL with the old slug
    response = client.get(
        reverse(
            "pontoon.translate",
            kwargs={"project": old_slug, "locale": "en", "resource": resource_path},
        )
    )
    # The old slug should cause a redirect to the new slug URL
    assert response.status_code == 302
    assert response.url == reverse(
        "pontoon.translate",
        kwargs={"project": new_slug, "locale": "en", "resource": resource_path},
    )


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
