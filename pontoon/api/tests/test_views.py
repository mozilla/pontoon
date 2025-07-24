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

    assert response.data == {
        "code": "kg",
        "name": "Klingon",
        "direction": "ltr",
        "population": 0,
        "cldr_plurals": "",
        "plural_rule": "",
        "script": "Latin",
        "google_translate_code": "",
        "ms_terminology_code": "",
        "ms_translator_code": "",
        "systran_translate_code": "",
        "team_description": "",
        "total_strings": 0,
        "approved_strings": 0,
        "pretranslated_strings": 0,
        "strings_with_warnings": 0,
        "strings_with_errors": 0,
        "missing_strings": 0,
        "unreviewed_strings": 0,
        "complete": True,
        "projects": ["terminology"],
    }


@pytest.mark.django_db
def test_locales(django_assert_num_queries):
    LocaleFactory.create_batch(3)

    with django_assert_num_queries(3):
        response = APIClient().get("/api/v2/locales/")

    assert response.status_code == 200

    locale_af = {
        "code": "af",
        "name": "Afrikaans",
        "direction": "ltr",
        "population": 8643000,
        "cldr_plurals": "1,5",
        "plural_rule": "(n != 1)",
        "script": "Latin",
        "google_translate_code": "af",
        "ms_terminology_code": "af-za",
        "ms_translator_code": "af",
        "systran_translate_code": "",
        "team_description": "",
        "total_strings": 0,
        "approved_strings": 0,
        "pretranslated_strings": 0,
        "strings_with_warnings": 0,
        "strings_with_errors": 0,
        "missing_strings": 0,
        "unreviewed_strings": 0,
        "complete": True,
        "projects": ["terminology"],
    }
    assert locale_af in response.data["results"]


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
    assert response.data == {
        "slug": "project_a",
        "name": "Project A",
        "priority": 1,
        "deadline": None,
        "visibility": "public",
        "contact": None,
        "info": "",
        "system_project": False,
        "disabled": False,
        "sync_disabled": False,
        "pretranslation_enabled": False,
        "total_strings": 0,
        "approved_strings": 0,
        "pretranslated_strings": 0,
        "strings_with_warnings": 0,
        "strings_with_errors": 0,
        "missing_strings": 0,
        "unreviewed_strings": 0,
        "complete": True,
        "tags": [],
        "localizations": {},
    }


@pytest.mark.django_db
def test_regular_projects(
    django_assert_num_queries,
):
    ProjectFactory.create_batch(3, disabled=True)
    ProjectFactory.create_batch(3, system_project=True)
    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/")

    assert response.status_code == 200

    expected_results = [
        {
            "slug": p.slug,
            "name": p.name,
            "priority": p.priority,
            "deadline": p.deadline,
            "visibility": p.visibility,
            "contact": p.contact,
            "info": p.info,
            "system_project": p.system_project,
            "disabled": p.disabled,
            "sync_disabled": p.sync_disabled,
            "pretranslation_enabled": p.pretranslation_enabled,
            "total_strings": p.total_strings,
            "approved_strings": p.approved_strings,
            "pretranslated_strings": p.pretranslated_strings,
            "strings_with_warnings": p.strings_with_warnings,
            "strings_with_errors": p.strings_with_errors,
            "missing_strings": p.missing_strings,
            "unreviewed_strings": p.unreviewed_strings,
            "complete": p.complete,
            "tags": [
                tag.name for tag in sorted(p.tags.all(), key=lambda tag: tag.name)
            ],
            "locales": [
                locale.code
                for locale in sorted(p.locales.all(), key=lambda locale: locale.code)
            ],
        }
        for p in sorted(
            Project.objects.filter(disabled=False, system_project=False),
            key=lambda p: p.pk,
        )
    ]

    for project in response.data["results"]:
        project["locales"] = sorted(project["locales"])
        project["tags"] = sorted(project["tags"])

    results = sorted(response.data["results"], key=lambda p: p["slug"])
    expected_results = sorted(expected_results, key=lambda p: p["slug"])

    # includes Terminology project
    assert response.data["count"] == 1
    assert results == expected_results


@pytest.mark.django_db
def test_all_projects(
    django_assert_num_queries,
):
    ProjectFactory.create_batch(3, disabled=True)
    ProjectFactory.create_batch(3, system_project=True)
    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/?include_system&include_disabled")

    assert response.status_code == 200

    expected_results = [
        {
            "slug": p.slug,
            "name": p.name,
            "priority": p.priority,
            "deadline": p.deadline,
            "visibility": p.visibility,
            "contact": p.contact,
            "info": p.info,
            "system_project": p.system_project,
            "disabled": p.disabled,
            "sync_disabled": p.sync_disabled,
            "pretranslation_enabled": p.pretranslation_enabled,
            "total_strings": p.total_strings,
            "approved_strings": p.approved_strings,
            "pretranslated_strings": p.pretranslated_strings,
            "strings_with_warnings": p.strings_with_warnings,
            "strings_with_errors": p.strings_with_errors,
            "missing_strings": p.missing_strings,
            "unreviewed_strings": p.unreviewed_strings,
            "complete": p.complete,
        }
        for p in sorted(Project.objects.all(), key=lambda p: p.pk)
    ]

    for project in response.data["results"]:
        project.pop("locales", None)
        project.pop("tags", None)

    results = sorted(response.data["results"], key=lambda p: p["slug"])
    expected_results = sorted(expected_results, key=lambda p: p["slug"])

    # includes Terminology project
    assert response.data["count"] == 8
    assert results == expected_results


@pytest.mark.django_db
def test_system_projects(
    django_assert_num_queries,
):
    ProjectFactory.create_batch(3, disabled=True)
    ProjectFactory.create_batch(3, system_project=True)
    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/?include_system")

    assert response.status_code == 200

    expected_results = [
        {
            "slug": p.slug,
            "name": p.name,
            "priority": p.priority,
            "deadline": p.deadline,
            "visibility": p.visibility,
            "contact": p.contact,
            "info": p.info,
            "system_project": p.system_project,
            "disabled": p.disabled,
            "sync_disabled": p.sync_disabled,
            "pretranslation_enabled": p.pretranslation_enabled,
            "total_strings": p.total_strings,
            "approved_strings": p.approved_strings,
            "pretranslated_strings": p.pretranslated_strings,
            "strings_with_warnings": p.strings_with_warnings,
            "strings_with_errors": p.strings_with_errors,
            "missing_strings": p.missing_strings,
            "unreviewed_strings": p.unreviewed_strings,
            "complete": p.complete,
        }
        for p in sorted(
            Project.objects.filter(system_project=True)
            | Project.objects.filter(disabled=False, system_project=False),
            key=lambda p: p.pk,
        )
    ]

    for project in response.data["results"]:
        project.pop("locales", None)
        project.pop("tags", None)

    results = sorted(response.data["results"], key=lambda p: p["slug"])
    expected_results = sorted(expected_results, key=lambda p: p["slug"])

    # includes Terminology, Tutorial and 3 system projects
    assert response.data["count"] == 5
    assert results == expected_results


@pytest.mark.django_db
def test_disabled_projects(
    django_assert_num_queries,
):
    ProjectFactory.create_batch(3, disabled=True)
    ProjectFactory.create_batch(3, system_project=True)
    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/?include_disabled")

        assert response.status_code == 200

    expected_results = [
        {
            "slug": p.slug,
            "name": p.name,
            "priority": p.priority,
            "deadline": p.deadline,
            "visibility": p.visibility,
            "contact": p.contact,
            "info": p.info,
            "system_project": p.system_project,
            "disabled": p.disabled,
            "sync_disabled": p.sync_disabled,
            "pretranslation_enabled": p.pretranslation_enabled,
            "total_strings": p.total_strings,
            "approved_strings": p.approved_strings,
            "pretranslated_strings": p.pretranslated_strings,
            "strings_with_warnings": p.strings_with_warnings,
            "strings_with_errors": p.strings_with_errors,
            "missing_strings": p.missing_strings,
            "unreviewed_strings": p.unreviewed_strings,
            "complete": p.complete,
        }
        for p in sorted(
            Project.objects.filter(disabled=True)
            | Project.objects.filter(disabled=False, system_project=False),
            key=lambda p: p.pk,
        )
    ]

    for project in response.data["results"]:
        project.pop("locales", None)
        project.pop("tags", None)

    results = sorted(response.data["results"], key=lambda p: p["slug"])
    expected_results = sorted(expected_results, key=lambda p: p["slug"])

    # includes Terminology and 3 other disabled projects
    assert response.data["count"] == 4
    assert results == expected_results


@pytest.mark.django_db
def test_project_locale():
    response = APIClient().get(
        "/api/v2/af/terminology/", HTTP_ACCEPT="application/json"
    )
    assert response.status_code == 200

    assert response.data == {
        "locale": {
            "code": "af",
            "name": "Afrikaans",
            "direction": "ltr",
            "population": 8643000,
            "cldr_plurals": "1,5",
            "plural_rule": "(n != 1)",
            "script": "Latin",
            "google_translate_code": "af",
            "ms_terminology_code": "af-za",
            "ms_translator_code": "af",
            "systran_translate_code": "",
            "team_description": "",
            "total_strings": 0,
            "approved_strings": 0,
            "pretranslated_strings": 0,
            "strings_with_warnings": 0,
            "strings_with_errors": 0,
            "missing_strings": 0,
            "unreviewed_strings": 0,
            "complete": True,
        },
        "total_strings": 0,
        "approved_strings": 0,
        "pretranslated_strings": 0,
        "strings_with_warnings": 0,
        "strings_with_errors": 0,
        "missing_strings": 0,
        "unreviewed_strings": 0,
        "complete": True,
        "project": {
            "slug": "terminology",
            "name": "Terminology",
            "priority": 1,
            "deadline": None,
            "visibility": "public",
            "contact": None,
            "info": "A project used to localize terminology.",
            "system_project": False,
            "disabled": False,
            "sync_disabled": True,
            "pretranslation_enabled": False,
            "total_strings": 0,
            "approved_strings": 0,
            "pretranslated_strings": 0,
            "strings_with_warnings": 0,
            "strings_with_errors": 0,
            "missing_strings": 0,
            "unreviewed_strings": 0,
            "complete": True,
        },
    }


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

    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "definition": "Allow access",
                "part_of_speech": "verb",
                "text": "open",
                "translation_text": "odpreti",
                "usage": "Open the door.",
                "notes": "",
            }
        ],
    }


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

    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "locale": "kg",
                "project": "project_a",
                "source": "Hello",
                "target": "Hola",
            }
        ],
    }
