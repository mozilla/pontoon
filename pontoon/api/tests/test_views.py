import pytest

from rest_framework.test import APIClient

from pontoon.base.models.project import Project
from pontoon.base.models.translation_memory import TranslationMemoryEntry
from pontoon.terminology.models import Term, TermTranslation
from pontoon.test import factories
from pontoon.test.factories import LocaleFactory, ProjectFactory


@pytest.mark.django_db
def test_locale():
    locale_a = factories.LocaleFactory(
        code="kg",
        name="Klingon",
    )
    response = APIClient().get(
        f"/api/v2/locales/{locale_a.code}/", HTTP_ACCEPT="application/json"
    )
    assert response.status_code == 200
    assert isinstance(response.data, dict)


@pytest.mark.django_db
def test_locales(django_assert_num_queries):
    LocaleFactory.create_batch(3)

    with django_assert_num_queries(3):
        response = APIClient().get("/api/v2/locales/")

    assert isinstance(response.data, dict)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project():
    project_a = factories.ProjectFactory(
        slug="project_a",
        name="Project A",
        repositories=[],
    )
    response = APIClient().get(
        f"/api/v2/projects/{project_a.slug}/", HTTP_ACCEPT="application/json"
    )
    assert response.status_code == 200
    assert isinstance(response.data, dict)


@pytest.mark.django_db
def test_projects(
    django_assert_num_queries,
):
    ProjectFactory.create_batch(3, visibility=Project.Visibility.PUBLIC) + list(
        Project.objects.filter(slug__in=["terminology"])
    )
    ProjectFactory.create_batch(3, disabled=True)
    ProjectFactory.create_batch(3, system_project=True) + list(
        Project.objects.filter(slug__in=["tutorial"])
    )

    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/")

    assert isinstance(response.data, dict)
    assert response.status_code == 200


@pytest.mark.django_db
def test_projects_flags(
    django_assert_num_queries,
):
    ProjectFactory.create_batch(3, visibility=Project.Visibility.PUBLIC) + list(
        Project.objects.filter(slug__in=["terminology"])
    )
    ProjectFactory.create_batch(3, disabled=True)
    ProjectFactory.create_batch(3, system_project=True) + list(
        Project.objects.filter(slug__in=["tutorial"])
    )
    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/?include_system&include_disabled")

    assert isinstance(response.data, dict)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_locale():
    response = APIClient().get(
        "/api/v2/af/terminology/", HTTP_ACCEPT="application/json"
    )
    assert response.status_code == 200
    assert isinstance(response.data, dict)


@pytest.mark.django_db
def test_terminology_search(django_assert_num_queries):
    locale_a = factories.LocaleFactory(
        code="kg",
        name="Klingon",
    )
    term1 = Term.objects.create(
        text="open",
        part_of_speech="verb",
        definition="Allow access",
        usage="Open the door.",
    )
    term2 = Term.objects.create(
        text="close",
        part_of_speech="verb",
        definition="Shut or block access",
        usage="Close the door.",
    )

    TermTranslation.objects.create(term=term1, locale=locale_a, text="odpreti")
    TermTranslation.objects.create(term=term2, locale=locale_a, text="zapreti")

    with django_assert_num_queries(5):
        response = APIClient().get("/api/v2/search/terminology/?text=open&locale=kg")

    assert response.status_code == 200
    assert isinstance(response.data, dict)


@pytest.mark.django_db
def test_tm_search(django_assert_num_queries):
    locale_a = factories.LocaleFactory(
        code="kg",
        name="Klingon",
    )
    project_a = factories.ProjectFactory(
        slug="project_a",
        name="Project A",
        repositories=[],
    )
    locale_b = factories.LocaleFactory(
        code="gs",
        name="Geonosian",
    )
    project_b = factories.ProjectFactory(slug="project_b", name="Project B")
    TranslationMemoryEntry.objects.create(
        source="Hello",
        target="Hola",
        locale=locale_a,
        project=project_a,
    )
    TranslationMemoryEntry.objects.create(
        source="Goodbye",
        target="Adiós",
        locale=locale_a,
        project=project_b,
    )
    TranslationMemoryEntry.objects.create(
        source="Hello",
        target="Bonjour",
        locale=locale_b,
        project=project_b,
    )

    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/search/tm/?text=hello&locale=kg")

    assert response.status_code == 200
    assert isinstance(response.data, dict)
