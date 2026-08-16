import pytest

from django.urls import reverse

from pontoon.base.models import Resource
from pontoon.test.factories import TranslatedResourceFactory
from pontoon.translate.views import get_preferred_locale


@pytest.fixture
def translated_resource_a(resource_a, locale_a):
    return TranslatedResourceFactory.create(resource=resource_a, locale=locale_a)


@pytest.fixture
def user_arabic(user_a):
    user_a.profile.custom_homepage = "ar"
    user_a.save()
    return user_a


@pytest.mark.django_db
def test_translate_template(client, project_locale_a, resource_a):
    url = reverse(
        "pontoon.translate",
        kwargs={
            "locale": project_locale_a.locale.code,
            "project": project_locale_a.project.slug,
            "resource": "all-resources",
        },
    )

    response = client.get(url)
    assert b"Pontoon" in response.content


@pytest.mark.django_db
def test_translate_validate_parameters(
    client, project_locale_a, resource_a, translated_resource_a
):
    url_invalid = reverse(
        "pontoon.translate",
        kwargs={"locale": "locale", "project": "project", "resource": "resource"},
    )

    url_valid = reverse(
        "pontoon.translate",
        kwargs={
            "locale": project_locale_a.locale.code,
            "project": project_locale_a.project.slug,
            "resource": resource_a.path,
        },
    )

    response = client.get(url_invalid)
    assert response.status_code == 404

    response = client.get(url_valid)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_preferred_locale_from_user_prefs(rf, user_arabic):
    # This user has 'ar' set as their favorite locale.
    rf.user = user_arabic
    locale = get_preferred_locale(rf)

    assert locale == "ar"


@pytest.mark.django_db
def test_get_preferred_locale_default(rf, user_a):
    # This user has no preferred locale set.
    rf.user = user_a
    locale = get_preferred_locale(rf)

    assert locale is None


@pytest.mark.django_db
def test_translate_invalid_locale_project(client):
    """If the locale and project are both invalid, return a 404."""
    response = client.get("/invalid-locale/invalid-project/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_translate_invalid_locale(client, resource_a):
    """
    If the project is valid but the locale isn't, redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get(
        f"/invalid-locale/{resource_a.project.slug}/{resource_a.path}/"
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_translate_invalid_project(
    client,
    resource_a,
    locale_a,
):
    """If the project is invalid, redirect home."""
    # this doesnt seem to redirect as the comment suggests
    response = client.get(f"/{locale_a.code}/invalid-project/{resource_a.path}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_translate_invalid_pl(
    client,
    locale_a,
    project_b,
):
    """
    If the requested locale is not available for this project,
    redirect home.
    """
    # this doesnt seem to redirect as the comment suggests
    response = client.get(f"/{locale_a.code}/{project_b.slug}/path/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_translate_invalid_resource(client, project_locale_a, resource_a):
    """
    A path that is not a resource of the project is a 404.
    """
    response = client.get(
        f"/{project_locale_a.locale.code}/{project_locale_a.project.slug}/no/such/path.ftl/"
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_translate_resource_not_translated_for_locale(
    client, project_locale_a, resource_a
):
    """
    A resource the locale has no TranslatedResource for is a 404 too.
    """
    response = client.get(
        f"/{project_locale_a.locale.code}/{project_locale_a.project.slug}/{resource_a.path}/"
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_translate_obsolete_resource(
    client, project_locale_a, resource_a, translated_resource_a
):
    """
    A resource that is gone from the repository is a 404 as well.
    """
    Resource.objects.filter(pk=resource_a.pk).mark_as_obsolete()

    response = client.get(
        f"/{project_locale_a.locale.code}/{project_locale_a.project.slug}/{resource_a.path}/"
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_translate_all_projects_path(client, project_locale_a, resource_a):
    """
    In the All Projects view, only `all-resources` is allowed.
    """
    locale = project_locale_a.locale.code

    response = client.get(f"/{locale}/all-projects/all-resources/")
    assert response.status_code == 200

    response = client.get(f"/{locale}/all-projects/{resource_a.path}/")
    assert response.status_code == 404

    response = client.get(f"/{locale}/all-projects/no/such/path.ftl/")
    assert response.status_code == 404
