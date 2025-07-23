import pytest

from rest_framework.test import APIClient

from pontoon.base.models.project import Project
from pontoon.base.models.translation_memory import TranslationMemoryEntry
from pontoon.terminology.models import Term, TermTranslation
from pontoon.test.factories import LocaleFactory, ProjectFactory


@pytest.fixture
def locales():
    return LocaleFactory.create_batch(3)


@pytest.fixture()
def regular_projects(locale_a):
    return ProjectFactory.create_batch(3, visibility=Project.Visibility.PUBLIC) + list(
        Project.objects.filter(slug__in=["terminology"])
    )


@pytest.fixture()
def disabled_projects(locale_a):
    return ProjectFactory.create_batch(3, disabled=True)


@pytest.fixture()
def system_projects(locale_a):
    return ProjectFactory.create_batch(3, system_project=True) + list(
        Project.objects.filter(slug__in=["tutorial"])
    )


@pytest.fixture
def terms(locale_a):
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

    return [term1, term2]


@pytest.fixture
def tm_entries(locale_a, locale_b, project_a, project_b):
    entry1 = TranslationMemoryEntry.objects.create(
        source="Hello",
        target="Hola",
        locale=locale_a,
        project=project_a,
    )
    entry2 = TranslationMemoryEntry.objects.create(
        source="Goodbye",
        target="Adiós",
        locale=locale_a,
        project=project_b,
    )
    entry3 = TranslationMemoryEntry.objects.create(
        source="Hello",
        target="Bonjour",
        locale=locale_b,
        project=project_b,
    )
    return [entry1, entry2, entry3]


# @pytest.fixture()
# def private_projects():
#     return ProjectFactory.create_batch(3, visibility=Project.Visibility.PRIVATE)


@pytest.mark.django_db
def test_locale(locale_a):
    response = APIClient().get(
        f"/api/v2/locales/{locale_a.code}/", HTTP_ACCEPT="application/json"
    )
    assert response.status_code == 200
    assert isinstance(response.data, dict)


@pytest.mark.django_db
def test_locales_optimization(django_assert_num_queries, locales):
    with django_assert_num_queries(3):
        response = APIClient().get("/api/v2/locales/")

    assert isinstance(response.data, dict)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project(project_a):
    response = APIClient().get(
        f"/api/v2/projects/{project_a.slug}/", HTTP_ACCEPT="application/json"
    )
    assert response.status_code == 200
    assert isinstance(response.data, dict)


@pytest.mark.django_db
def test_projects_optimization(
    django_assert_num_queries,
    regular_projects,
    disabled_projects,
    system_projects,
):
    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/")

    assert isinstance(response.data, dict)
    assert response.status_code == 200
    # assert len(response["data"]["result"]) == 3


@pytest.mark.django_db
def test_projects_flags_optimization(
    django_assert_num_queries,
    regular_projects,
    disabled_projects,
    system_projects,
):
    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/?includeSystem&includeDisabled")

    assert isinstance(response.data, dict)
    assert response.status_code == 200


# NON FUNCTIONAL
# @pytest.mark.django_db
# def test_project_locale(project_locale_a, project_a, locale_a):

#     response = APIClient().get(f"/api/v2/{project_locale_a.locale.code}/{project_locale_a.project.slug}/", HTTP_ACCEPT="application/json")
#     assert project_locale_a.project == project_a
#     assert project_locale_a.locale == locale_a
#     assert response.status_code == 200
#     assert isinstance(response.data, dict)


@pytest.mark.django_db
def test_terminology_search_optimization(django_assert_num_queries, terms):
    with django_assert_num_queries(5):
        response = APIClient().get("/api/v2/search/terminology/?text=open&locale=kg")

    assert response.status_code == 200
    assert isinstance(response.data, dict)


@pytest.mark.django_db
def test_tm_search_optimization(django_assert_num_queries, tm_entries):
    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/search/tm/?text=hello&locale=kg")

    assert response.status_code == 200
    assert isinstance(response.data, dict)
