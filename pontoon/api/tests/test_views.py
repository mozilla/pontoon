import pytest

from rest_framework.test import APIClient

from django.db.models import Prefetch

from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.resource import Resource
from pontoon.base.models.translation_memory import TranslationMemoryEntry
from pontoon.terminology.models import Term, TermTranslation
from pontoon.test.factories import (
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslatedResourceFactory,
)


@pytest.mark.django_db
def test_locale(django_assert_num_queries):
    locale_a = LocaleFactory(
        code="kg",
        name="Klingon",
    )
    project_a = ProjectFactory(
        slug="project_a",
        name="Project A",
        repositories=[],
    )
    resource_a = ResourceFactory(project=project_a, path="resource_a.po", format="po")

    translated_resource_a = TranslatedResourceFactory.create(
        locale=locale_a,
        resource=resource_a,
    )

    translated_resource_a.total_strings = 25
    translated_resource_a.approved_strings = 15
    translated_resource_a.pretranslated_strings = 0
    translated_resource_a.strings_with_errors = 3
    translated_resource_a.strings_with_warnings = 2
    translated_resource_a.missing_strings = 5
    translated_resource_a.unreviewed_strings = 5
    translated_resource_a.save()

    with django_assert_num_queries(2):
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
        "total_strings": 25,
        "approved_strings": 15,
        "pretranslated_strings": 0,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "complete": False,
        "projects": ["terminology"],
    }


@pytest.mark.django_db
def test_locales(django_assert_num_queries):
    project_a = ProjectFactory(
        slug="project_a",
        name="Project A",
    )
    project_b = ProjectFactory(
        slug="project_b",
        name="Project B",
    )

    locales = LocaleFactory.create_batch(3)

    resources = [
        ResourceFactory.create(
            project=project_a, path=f"resource_{project_a.slug}.po", format="po"
        ),
        ResourceFactory.create(
            project=project_b, path=f"resource_{project_b.slug}.po", format="po"
        ),
    ]

    translated_resources = [
        TranslatedResourceFactory.create(locale=locale, resource=resources[0])
        for locale in locales
    ] + [
        TranslatedResourceFactory.create(locale=locale, resource=resources[1])
        for locale in locales
    ]

    for translated_resource in translated_resources:
        translated_resource.total_strings = 25
        translated_resource.approved_strings = 15
        translated_resource.pretranslated_strings = 0
        translated_resource.strings_with_errors = 3
        translated_resource.strings_with_warnings = 2
        translated_resource.missing_strings = 5
        translated_resource.unreviewed_strings = 5
        translated_resource.save()

    expected_results = [
        {
            "code": loc.code,
            "name": loc.name,
            "direction": loc.direction,
            "population": loc.population,
            "cldr_plurals": loc.cldr_plurals,
            "plural_rule": loc.plural_rule,
            "script": loc.script,
            "google_translate_code": loc.google_translate_code,
            "ms_terminology_code": loc.ms_terminology_code,
            "ms_translator_code": loc.ms_translator_code,
            "systran_translate_code": loc.systran_translate_code,
            "team_description": loc.team_description,
            "total_strings": loc.total_strings,
            "approved_strings": loc.approved_strings,
            "pretranslated_strings": loc.pretranslated_strings,
            "strings_with_warnings": loc.strings_with_warnings,
            "strings_with_errors": loc.strings_with_errors,
            "missing_strings": loc.missing_strings,
            "unreviewed_strings": loc.unreviewed_strings,
            "complete": loc.complete,
        }
        for loc in sorted(
            Locale.objects.prefetch_related(
                Prefetch(
                    "project_locale",
                    queryset=ProjectLocale.objects.visible().select_related("project"),
                    to_attr="fetched_project_locales",
                )
            )
            .distinct()
            .filter(
                translatedresources__resource__project__disabled=False,
                translatedresources__resource__project__system_project=False,
                translatedresources__resource__project__visibility="public",
            ),
            key=lambda loc: loc.pk,
        )
    ]

    with django_assert_num_queries(3):
        response = APIClient().get("/api/v2/locales/")

    assert response.status_code == 200

    for locale in response.data["results"]:
        locale.pop("projects", None)

    results = sorted(response.data["results"], key=lambda loc: loc["code"])

    # Split the expected results to match pagination limit of 100
    expected_results = sorted(expected_results, key=lambda loc: loc["code"])[:100]

    assert response.data["count"] == 111

    assert results == expected_results


@pytest.mark.django_db
def test_project(django_assert_num_queries):
    locale_a = LocaleFactory(
        code="kg",
        name="Klingon",
    )
    project_a = ProjectFactory(
        slug="project_a",
        name="Project A",
        repositories=[],
    )
    resource_a = ResourceFactory(project=project_a, path="resource_a.po", format="po")

    translated_resource_a = TranslatedResourceFactory.create(
        locale=locale_a,
        resource=resource_a,
    )

    translated_resource_a.total_strings = 25
    translated_resource_a.approved_strings = 15
    translated_resource_a.pretranslated_strings = 0
    translated_resource_a.strings_with_errors = 3
    translated_resource_a.strings_with_warnings = 2
    translated_resource_a.missing_strings = 5
    translated_resource_a.unreviewed_strings = 5
    translated_resource_a.save()

    with django_assert_num_queries(4):
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
        "total_strings": 25,
        "approved_strings": 15,
        "pretranslated_strings": 0,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "complete": False,
        "tags": [],
        "localizations": {},
    }


@pytest.mark.django_db
def test_projects(django_assert_num_queries):
    locale_a = LocaleFactory(
        code="kg",
        name="Klingon",
    )
    locale_b = LocaleFactory(code="hut", name="Huttese")

    projects = ProjectFactory.create_batch(3, disabled=True)
    ProjectFactory.create_batch(3, system_project=True)

    project_1 = projects[0]
    project_2 = projects[1]

    # append extra Resource to simulate multiple resource per project
    resources = [
        ResourceFactory.create(
            project=project, path=f"resource_{project.slug}.po", format="po"
        )
        for project in Project.objects.all()
    ] + [ResourceFactory.create(project=project_1, path="resource_a_2.po", format="po")]

    # append extra TranslatedResource to simulate multiple Translated Resources per project
    translated_resources = [
        TranslatedResourceFactory.create(locale=locale_a, resource=resource)
        for resource in resources
    ] + [
        TranslatedResourceFactory.create(
            locale=locale_b, resource=Resource.objects.filter(project=project_2).first()
        )
    ]

    for translated_resource in translated_resources:
        translated_resource.total_strings = 25
        translated_resource.approved_strings = 15
        translated_resource.pretranslated_strings = 0
        translated_resource.strings_with_errors = 3
        translated_resource.strings_with_warnings = 2
        translated_resource.missing_strings = 5
        translated_resource.unreviewed_strings = 5
        translated_resource.save()

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

    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/?include_system&include_disabled")

    assert response.status_code == 200

    for project in response.data["results"]:
        project.pop("locales", None)
        project.pop("tags", None)

    results = sorted(response.data["results"], key=lambda p: p["slug"])
    expected_results = sorted(expected_results, key=lambda p: p["slug"])

    # includes Terminology, Tutorial project
    assert response.data["count"] == 8
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
def test_project_locale(django_assert_num_queries):
    locale_af = Locale.objects.get(code="af")
    locale_a = LocaleFactory(
        code="kg",
        name="Klingon",
    )
    project = Project.objects.get(slug="terminology")
    # append extra Resource to simulate multiple resource per project
    resources = [
        ResourceFactory.create(
            project=project, path=f"resource_{project.slug}_1.po", format="po"
        ),
        ResourceFactory.create(
            project=project, path=f"resource_{project.slug}_2.po", format="po"
        ),
    ]

    # append extra TranslatedResource to simulate multiple Translated Resources per project
    translated_resources = [
        TranslatedResourceFactory.create(locale=locale_af, resource=resources[0]),
        TranslatedResourceFactory.create(locale=locale_a, resource=resources[1]),
    ]

    for translated_resource in translated_resources:
        translated_resource.total_strings = 25
        translated_resource.approved_strings = 15
        translated_resource.pretranslated_strings = 0
        translated_resource.strings_with_errors = 3
        translated_resource.strings_with_warnings = 2
        translated_resource.missing_strings = 5
        translated_resource.unreviewed_strings = 5
        translated_resource.save()

    with django_assert_num_queries(6):
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
            "total_strings": 25,
            "approved_strings": 15,
            "pretranslated_strings": 0,
            "strings_with_warnings": 2,
            "strings_with_errors": 3,
            "missing_strings": 5,
            "unreviewed_strings": 5,
            "complete": False,
        },
        "total_strings": 25,
        "approved_strings": 15,
        "pretranslated_strings": 0,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "complete": False,
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
            "total_strings": 50,
            "approved_strings": 30,
            "pretranslated_strings": 0,
            "strings_with_warnings": 4,
            "strings_with_errors": 6,
            "missing_strings": 10,
            "unreviewed_strings": 10,
            "complete": False,
        },
    }


@pytest.mark.django_db
def test_terminology_search(django_assert_num_queries):
    locale_a = LocaleFactory(
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
    locale_a = LocaleFactory(
        code="kg",
        name="Klingon",
    )
    project_a = ProjectFactory(
        slug="project_a",
        name="Project A",
        repositories=[],
    )
    locale_b = LocaleFactory(
        code="gs",
        name="Geonosian",
    )
    project_b = ProjectFactory(slug="project_b", name="Project B")
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
