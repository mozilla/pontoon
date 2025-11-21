import pytest

from rest_framework.test import APIClient

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.db.models import Prefetch
from django.utils.timezone import now, timedelta

from pontoon.api.models import PersonalAccessToken
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.resource import Resource
from pontoon.base.models.translation_memory import TranslationMemoryEntry
from pontoon.terminology.models import Term, TermTranslation
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)


@pytest.mark.django_db
def test_user_actions_project_not_visible(member):
    client = APIClient()
    client.force_authenticate(user=member.user)

    private_project = ProjectFactory(
        slug="private-project",
        visibility="private",
    )

    date = now().strftime("%Y-%m-%d")

    response = client.get(
        f"/api/v2/user-actions/{date}/project/{private_project.slug}/",
        HTTP_ACCEPT="application/json",
    )

    assert response.status_code == 403
    assert response.data == {
        "detail": "You do not have permission to access data for this project."
    }


@pytest.mark.django_db
def test_dynamic_fields(django_assert_num_queries):
    expected_results = [
        {
            "code": loc.code,
            "name": loc.name,
        }
        for loc in (
            Locale.objects.filter(
                translatedresources__resource__project__disabled=False,
                translatedresources__resource__project__system_project=False,
                translatedresources__resource__project__visibility="public",
            ).order_by("code")
        )
    ][:100]

    with django_assert_num_queries(2):
        response = APIClient().get("/api/v2/locales/?fields=code,name")

    results = sorted(response.data["results"], key=lambda loc: loc["code"])

    assert response.status_code == 200
    assert response.data["count"] == 108
    assert results == expected_results


@pytest.mark.django_db
def test_dynamic_page_sizes(django_assert_num_queries):
    for page in range(1, 3):
        with django_assert_num_queries(3):
            response = APIClient().get(f"/api/v2/locales/?page_size=33&page={page}")

        assert response.status_code == 200
        assert len(response.data["results"]) == 33

    with django_assert_num_queries(3):
        response = APIClient().get("/api/v2/locales/?page_size=33&page=4")

    assert response.data["count"] == 108
    assert response.status_code == 200
    assert len(response.data["results"]) == 9


@pytest.mark.django_db
def test_locale(django_assert_num_queries):
    locale_a = LocaleFactory(
        code="kg",
        name="Klingon",
    )
    project_terminology = Project.objects.get(slug="terminology")

    resource = ResourceFactory.create(
        project=project_terminology,
        path=f"resource_{project_terminology.slug}_1.po",
        format="gettext",
    )

    # append extra TranslatedResource to simulate multiple Translated Resources per project
    translated_resource = TranslatedResourceFactory.create(
        locale=locale_a, resource=resource
    )

    translated_resource.total_strings = 25
    translated_resource.approved_strings = 15
    translated_resource.pretranslated_strings = 0
    translated_resource.strings_with_errors = 3
    translated_resource.strings_with_warnings = 2
    translated_resource.missing_strings = 5
    translated_resource.unreviewed_strings = 5
    translated_resource.save()

    with django_assert_num_queries(4):
        response = APIClient().get(
            f"/api/v2/locales/{locale_a.code}/", HTTP_ACCEPT="application/json"
        )

    assert response.status_code == 200

    localizations = response.data.pop("localizations", None)

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

    assert {
        "project": {
            "slug": "terminology",
            "name": "Terminology",
        },
        "total_strings": 25,
        "approved_strings": 15,
        "pretranslated_strings": 0,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "complete": False,
    } in localizations


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
            project=project_a, path=f"resource_{project_a.slug}.po", format="gettext"
        ),
        ResourceFactory.create(
            project=project_b, path=f"resource_{project_b.slug}.po", format="gettext"
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
    locale_af = Locale.objects.get(code="af")
    locale_a = LocaleFactory(
        code="kg",
        name="Klingon",
    )
    project = Project.objects.get(slug="terminology")
    # append extra Resource to simulate multiple resource per project
    resources = [
        ResourceFactory.create(
            project=project, path=f"resource_{project.slug}_1.po", format="gettext"
        ),
        ResourceFactory.create(
            project=project, path=f"resource_{project.slug}_2.po", format="gettext"
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

    with django_assert_num_queries(5):
        response = APIClient().get(
            f"/api/v2/projects/{project.slug}/", HTTP_ACCEPT="application/json"
        )

    assert response.status_code == 200

    localizations = response.data.pop("localizations", None)
    assert response.data == {
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
        "tags": [],
        "locales": [
            "fur",
            "af",
            "pt",
            "an",
            "uz",
            "cy",
            "ca",
            "ms",
            "zu",
            "km",
            "da",
            "ko",
            "lv",
            "es-ES",
            "ast",
            "son",
            "fa",
            "kk",
            "eo",
            "nn-NO",
            "ar",
            "ne-NP",
            "ff",
            "ja",
            "ta",
            "nb-NO",
            "ro",
            "kn",
            "mn",
            "sr",
            "mai",
            "es-CL",
            "eu",
            "gd",
            "vi",
            "is",
            "hy-AM",
            "fy-NL",
            "sl",
            "si",
            "el",
            "es-MX",
            "es-AR",
            "sw",
            "uk",
            "gl",
            "nso",
            "fi",
            "it",
            "lt",
            "hsb",
            "bs",
            "ta-LK",
            "mr",
            "wo",
            "xh",
            "cs",
            "lij",
            "bn-IN",
            "ml",
            "ak",
            "bg",
            "mk",
            "pl",
            "te",
            "or",
            "hu",
            "ur",
            "be",
            "he",
            "th",
            "es",
            "ru",
            "ht",
            "gu-IN",
            "ilo",
            "hi-IN",
            "csb",
            "fr",
            "as",
            "az",
            "tr",
            "de",
            "br",
            "pa-IN",
            "ga",
            "bn-BD",
            "en-GB",
            "sk",
            "oc",
            "tl",
            "pt-PT",
            "nl",
            "ku",
            "dsb",
            "rm",
            "zh-CN",
            "pt-BR",
            "sv-SE",
            "et",
            "hr",
            "ga-IE",
            "id",
            "sq",
            "my",
            "en-ZA",
            "ka",
            "zh-TW",
            "kg",
        ],
    }

    assert {
        "locale": {
            "code": "kg",
            "name": "Klingon",
        },
        "total_strings": 25,
        "approved_strings": 15,
        "pretranslated_strings": 0,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "complete": False,
    } in localizations

    assert {
        "locale": {
            "code": "af",
            "name": "Afrikaans",
        },
        "total_strings": 25,
        "approved_strings": 15,
        "pretranslated_strings": 0,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "complete": False,
    } in localizations


@pytest.mark.django_db
def test_system_project(django_assert_num_queries):
    project = Project.objects.get(slug="tutorial")

    with django_assert_num_queries(5):
        response = APIClient().get(
            f"/api/v2/projects/{project.slug}/", HTTP_ACCEPT="application/json"
        )

    assert response.status_code == 200

    assert response.data["slug"] == "tutorial"
    assert response.data["name"] == "Tutorial"


@pytest.mark.django_db
def test_disabled_project(django_assert_num_queries):
    project = ProjectFactory.create(slug="disabled-1", disabled=True)

    with django_assert_num_queries(1):
        response = APIClient().get(
            f"/api/v2/projects/{project.slug}/", HTTP_ACCEPT="application/json"
        )

    assert response.status_code == 404


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
            project=project, path=f"resource_{project.slug}.po", format="gettext"
        )
        for project in Project.objects.all()
    ] + [ResourceFactory.create(project=project_1, path="resource_a_2.po", format="gettext")]

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
        response = APIClient().get(
            "/api/v2/projects/?include_system=True&include_disabled=True"
        )

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
        response = APIClient().get("/api/v2/projects/?include_system=True")

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
        response = APIClient().get("/api/v2/projects/?include_disabled=True")

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
def test_entity(django_assert_num_queries):
    project_a = ProjectFactory(
        slug="project_a",
        name="Project A",
    )

    resource = ResourceFactory.create(
        project=project_a, path=f"resource_{project_a.slug}.po", format="gettext"
    )

    entity = EntityFactory.create(string="Test String", resource=resource)

    with django_assert_num_queries(4):
        response = APIClient().get(
            f"/api/v2/entities/{entity.pk}/", HTTP_ACCEPT="application/json"
        )
    assert response.status_code == 200

    assert response.data == {
        "id": entity.pk,
        "key": [],
        "string": "Test String",
        "project": {"name": "Project A", "slug": "project_a"},
        "resource": {"path": "resource_project_a.po", "format": "gettext"},
    }


@pytest.mark.django_db
def test_entity_with_translations(django_assert_num_queries):
    project_a = ProjectFactory(
        slug="project_a",
        name="Project A",
    )

    locales = [
        LocaleFactory(
            code="kg",
            name="Klingon",
        ),
        LocaleFactory(code="hut", name="Huttese"),
        LocaleFactory(code="gs", name="Geonosian"),
    ]

    resource = ResourceFactory.create(
        project=project_a, path=f"resource_{project_a.slug}.po", format="gettext"
    )

    entity = EntityFactory.create(string="Test String", resource=resource)

    for locale in locales:
        (
            TranslationFactory.create(
                entity=entity,
                locale=locale,
                string=f"approved_translation_{locale.name}",
                approved=True,
            ),
        )
        TranslationFactory.create(
            entity=entity,
            locale=locale,
            string=f"suggested_translation_{locale.name}",
        )

    with django_assert_num_queries(4):
        response = APIClient().get(
            f"/api/v2/entities/{entity.pk}/?include_translations=True",
            HTTP_ACCEPT="application/json",
        )
    assert response.status_code == 200

    assert response.data == {
        "id": entity.pk,
        "string": "Test String",
        "key": [],
        "project": {"slug": "project_a", "name": "Project A"},
        "resource": {"path": "resource_project_a.po", "format": "gettext"},
        "translations": [
            {
                "locale": {"code": "kg", "name": "Klingon"},
                "string": "approved_translation_Klingon",
            },
            {
                "locale": {"code": "hut", "name": "Huttese"},
                "string": "approved_translation_Huttese",
            },
            {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "approved_translation_Geonosian",
            },
        ],
    }


@pytest.mark.django_db
def test_entity_alternate(django_assert_num_queries):
    project_a = ProjectFactory(
        slug="project_a",
        name="Project A",
    )

    project_b = ProjectFactory(
        slug="project_b",
        name="Project B",
    )

    resource_a = ResourceFactory.create(
        project=project_a, path=f"resource_{project_a.slug}.po", format="gettext"
    )

    resource_b = ResourceFactory.create(
        project=project_b, path=f"resource_{project_b.slug}.po", format="gettext"
    )

    entities = [
        EntityFactory.create(
            string="Test String A",
            resource=resource_a,
            key=["entityKey1", "entityKey2"],
        ),
        EntityFactory.create(
            string="Test String B", resource=resource_a, key=["entityKey3"]
        ),
        EntityFactory.create(
            string="Test String C", resource=resource_b, key=["entityKey4"]
        ),
    ]

    with django_assert_num_queries(4):
        response = APIClient().get(
            f"/api/v2/entities/{project_a.slug}/{resource_a.path}/{entities[0].key[0]}/",
            HTTP_ACCEPT="application/json",
        )
    assert response.status_code == 200

    assert response.data == {
        "id": entities[0].pk,
        "key": ["entityKey1", "entityKey2"],
        "string": "Test String A",
        "project": {"name": "Project A", "slug": "project_a"},
        "resource": {"path": "resource_project_a.po", "format": "gettext"},
    }


@pytest.mark.django_db
def test_entities(django_assert_num_queries):
    project_a = ProjectFactory(
        slug="project_a",
        name="Project A",
    )

    resource_a = ResourceFactory.create(
        project=project_a, path=f"resource_{project_a.slug}.po", format="gettext"
    )

    entities = [
        EntityFactory.create(string="Test String A", resource=resource_a),
        EntityFactory.create(string="Test String B", resource=resource_a),
        EntityFactory.create(string="Test String C", resource=resource_a),
    ]

    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/entities/", HTTP_ACCEPT="application/json")
    assert response.status_code == 200

    expected_data = [
        {
            "id": entity.pk,
            "string": entity.string,
            "key": entity.key,
            "project": {"slug": "project_a", "name": "Project A"},
            "resource": {"path": "resource_project_a.po", "format": "gettext"},
        }
        for entity in entities
    ]

    for entity in expected_data:
        assert entity in response.data["results"]


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
            project=project, path=f"resource_{project.slug}_1.po", format="gettext"
        ),
        ResourceFactory.create(
            project=project, path=f"resource_{project.slug}_2.po", format="gettext"
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
    locale_b = LocaleFactory(
        code="gs",
        name="Geonosian",
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
    term3 = Term.objects.create(
        text="opened",
        part_of_speech="verb",
        definition="Allow access (past tense)",
        usage="Opened the door.",
    )
    term4 = Term.objects.create(
        text="click",
        part_of_speech="verb",
        definition="press",
        usage="Click the button.",
    )

    TermTranslation.objects.create(term=term1, locale=locale_a, text="odpreti")
    TermTranslation.objects.create(term=term2, locale=locale_a, text="zapreti")
    TermTranslation.objects.create(term=term3, locale=locale_a, text="odprto")
    TermTranslation.objects.create(term=term4, locale=locale_b, text="klikni")

    with django_assert_num_queries(3):
        response = APIClient().get("/api/v2/search/terminology/?text=open&locale=kg")

    assert response.status_code == 200

    assert response.data == {
        "count": 2,
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
            },
            {
                "definition": "Allow access (past tense)",
                "part_of_speech": "verb",
                "text": "opened",
                "translation_text": "odprto",
                "usage": "Opened the door.",
                "notes": "",
            },
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
    resource_a = ResourceFactory.create(
        project=project_a,
        path=f"resource_{project_a.slug}.po",
        format="gettext",
    )
    entity_a = EntityFactory.create(
        string="Entity A",
        resource=resource_a,
    )
    locale_b = LocaleFactory(
        code="gs",
        name="Geonosian",
    )
    project_b = ProjectFactory(
        slug="project_b",
        name="Project B",
    )
    resource_b = ResourceFactory.create(
        project=project_b,
        path=f"resource_{project_b.slug}.po",
        format="gettext",
    )
    entity_b = EntityFactory.create(
        string="Entity B",
        resource=resource_b,
    )
    project_private = ProjectFactory(
        slug="project_private",
        name="Project Private",
        visibility="private",
    )
    resource_private = ResourceFactory.create(
        project=project_private,
        path=f"resource_{project_private.slug}.po",
        format="gettext",
    )
    entity_private = EntityFactory.create(
        string="Entity Private",
        resource=resource_private,
    )
    TranslationMemoryEntry.objects.create(
        source="Hello",
        target="Hola",
        locale=locale_a,
        project=project_a,
        entity=entity_a,
    )
    TranslationMemoryEntry.objects.create(
        source="Goodbye",
        target="Adiós",
        locale=locale_a,
        project=project_b,
        entity=entity_b,
    )
    TranslationMemoryEntry.objects.create(
        source="Hello",
        target="Bonjour",
        locale=locale_b,
        project=project_b,
        entity=entity_b,
    )
    TranslationMemoryEntry.objects.create(
        source="Hello",
        target="Hola",
        locale=locale_a,
        project=project_private,
        entity=entity_private,
    )

    with django_assert_num_queries(2):
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
                "entity": entity_a.pk,
                "source": "Hello",
                "target": "Hola",
            }
        ],
    }


@pytest.mark.django_db
def test_translation_search(django_assert_num_queries):
    locale_a = LocaleFactory(code="gs", name="Geonosian")

    locale_b = LocaleFactory(code="kg", name="Klingon")

    project_a = ProjectFactory(slug="project-a", name="Project A")

    project_b = ProjectFactory(slug="project-b", name="Project B")

    resources = {
        "resource_a": ResourceFactory.create(
            project=project_a, path=f"resource_{project_a.slug}_1.po", format="gettext"
        ),
        "resource_b": ResourceFactory.create(
            project=project_a, path=f"resource_{project_a.slug}_2.ini", format="ini"
        ),
        "resource_c": ResourceFactory.create(
            project=project_b, path=f"resource_{project_b.slug}_3.ftl", format="ftl"
        ),
    }

    entities = {
        "entity_a": EntityFactory.create(
            string="the project_a test",
            resource=resources["resource_a"],
            key=["TestKey_A_squibble"],
        ),
        "entity_b": EntityFactory.create(
            string="the project_a Test",
            resource=resources["resource_a"],
            key=["TestKey_B_squibb"],
        ),
        "entity_c": EntityFactory.create(
            string="theproject_aTestsquibb",
            resource=resources["resource_a"],
            key=["TestKey_C dinglehopper"],
        ),
        "entity_d": EntityFactory.create(
            string="theproject_a Test", resource=resources["resource_a"]
        ),
        "entity_e": EntityFactory.create(
            string="the project_a test", resource=resources["resource_b"]
        ),
        "entity_f": EntityFactory.create(
            string="the project_a Flibbertigibbet Test",
            resource=resources["resource_b"],
        ),
        "entity_g": EntityFactory.create(
            string="the project_a test Flibbertigibbet",
            resource=resources["resource_b"],
            key=["TestKey_G dinglehopperite"],
        ),
        "entity_h": EntityFactory.create(
            string="the project_aTest Flibbertigibbet",
            resource=resources["resource_b"],
            key=["Test_H_dinglehopper"],
        ),
        "entity_i": EntityFactory.create(
            string="the project_b Test", resource=resources["resource_c"]
        ),
        "entity_j": EntityFactory.create(
            string="theproject_b Test Flibbertigibbet dinglehopper",
            resource=resources["resource_c"],
            key=["TestKey_J_squibble"],
        ),
        "entity_k": EntityFactory.create(
            string="the project_btest Flibbertigibbet dinglehopper",
            resource=resources["resource_c"],
            key=["TestKey_K_squibb"],
        ),
        "entity_l": EntityFactory.create(
            string="the project_b Test Flibbertigibbetelle Dinglehopper",
            resource=resources["resource_c"],
        ),
    }

    for entity in entities.values():
        TranslationFactory.create(
            entity=entity,
            locale=locale_a,
            string=f"translation_{locale_a.name}",
            approved=True,
        )

    for entity in (
        entities["entity_c"],
        entities["entity_g"],
        entities["entity_h"],
        entities["entity_k"],
        entities["entity_l"],
    ):
        TranslationFactory.create(
            entity=entity,
            locale=locale_b,
            string=f"translation_{locale_b.name}",
            approved=True,
        )

    # Test search without any parameters
    with django_assert_num_queries(0):
        response = APIClient().get(
            "/api/v2/search/translations/",
            HTTP_ACCEPT="application/json",
        )

    assert response.status_code == 400

    assert response.data == {
        "locale": ["This field is required."],
        "text": ["This field is required."],
    }

    # Test search without locale parameter
    with django_assert_num_queries(0):
        response = APIClient().get(
            "/api/v2/search/translations/?text=test",
            HTTP_ACCEPT="application/json",
        )

    assert response.status_code == 400

    assert response.data == {"locale": ["This field is required."]}

    # Test search with required parameters only
    with django_assert_num_queries(6):
        response = APIClient().get(
            f"/api/v2/search/translations/?text=Flibbertigibbetelle&locale={locale_a.code}",
            HTTP_ACCEPT="application/json",
        )

    assert response.status_code == 200

    assert response.data["results"] == [
        {
            "id": entities["entity_l"].id,
            "string": "the project_b Test Flibbertigibbetelle Dinglehopper",
            "key": [],
            "project": {"slug": "project-b", "name": "Project B"},
            "resource": {"path": "resource_project-b_3.ftl", "format": "ftl"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        }
    ]

    # Test search_match_whole_word parameter
    with django_assert_num_queries(6):
        response = APIClient().get(
            f"/api/v2/search/translations/?text=Flibbertigibbet&locale={locale_a.code}&search_match_whole_word=true",
            HTTP_ACCEPT="application/json",
        )

    assert response.status_code == 200

    assert response.data["results"] == [
        {
            "id": entities["entity_f"].id,
            "string": "the project_a Flibbertigibbet Test",
            "key": [],
            "project": {"slug": "project-a", "name": "Project A"},
            "resource": {"path": "resource_project-a_2.ini", "format": "ini"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_g"].id,
            "string": "the project_a test Flibbertigibbet",
            "key": ["TestKey_G dinglehopperite"],
            "project": {"slug": "project-a", "name": "Project A"},
            "resource": {"path": "resource_project-a_2.ini", "format": "ini"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_h"].id,
            "string": "the project_aTest Flibbertigibbet",
            "key": ["Test_H_dinglehopper"],
            "project": {"slug": "project-a", "name": "Project A"},
            "resource": {"path": "resource_project-a_2.ini", "format": "ini"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_j"].id,
            "string": "theproject_b Test Flibbertigibbet dinglehopper",
            "key": ["TestKey_J_squibble"],
            "project": {"slug": "project-b", "name": "Project B"},
            "resource": {"path": "resource_project-b_3.ftl", "format": "ftl"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_k"].id,
            "string": "the project_btest Flibbertigibbet dinglehopper",
            "key": ["TestKey_K_squibb"],
            "project": {"slug": "project-b", "name": "Project B"},
            "resource": {"path": "resource_project-b_3.ftl", "format": "ftl"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
    ]

    # Test search_match_case parameter
    with django_assert_num_queries(6):
        response = APIClient().get(
            f"/api/v2/search/translations/?text=Dinglehopper&locale={locale_a.code}&search_match_case=true",
            HTTP_ACCEPT="application/json",
        )

    assert response.status_code == 200

    assert response.data["results"] == [
        {
            "id": entities["entity_l"].id,
            "string": "the project_b Test Flibbertigibbetelle Dinglehopper",
            "key": [],
            "project": {"slug": "project-b", "name": "Project B"},
            "resource": {"path": "resource_project-b_3.ftl", "format": "ftl"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        }
    ]

    # Test search_identifiers parameter
    with django_assert_num_queries(6):
        response = APIClient().get(
            f"/api/v2/search/translations/?text=Dinglehopper&locale={locale_a.code}&search_identifiers=true",
            HTTP_ACCEPT="application/json",
        )

    assert response.status_code == 200

    assert response.data["results"] == [
        {
            "id": entities["entity_c"].id,
            "string": "theproject_aTestsquibb",
            "key": ["TestKey_C dinglehopper"],
            "project": {"slug": "project-a", "name": "Project A"},
            "resource": {"path": "resource_project-a_1.po", "format": "gettext"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_g"].id,
            "string": "the project_a test Flibbertigibbet",
            "key": ["TestKey_G dinglehopperite"],
            "project": {"slug": "project-a", "name": "Project A"},
            "resource": {"path": "resource_project-a_2.ini", "format": "ini"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_h"].id,
            "string": "the project_aTest Flibbertigibbet",
            "key": ["Test_H_dinglehopper"],
            "project": {"slug": "project-a", "name": "Project A"},
            "resource": {"path": "resource_project-a_2.ini", "format": "ini"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_j"].id,
            "string": "theproject_b Test Flibbertigibbet dinglehopper",
            "key": ["TestKey_J_squibble"],
            "project": {"slug": "project-b", "name": "Project B"},
            "resource": {"path": "resource_project-b_3.ftl", "format": "ftl"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_k"].id,
            "string": "the project_btest Flibbertigibbet dinglehopper",
            "key": ["TestKey_K_squibb"],
            "project": {"slug": "project-b", "name": "Project B"},
            "resource": {"path": "resource_project-b_3.ftl", "format": "ftl"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_l"].id,
            "string": "the project_b Test Flibbertigibbetelle Dinglehopper",
            "key": [],
            "project": {"slug": "project-b", "name": "Project B"},
            "resource": {"path": "resource_project-b_3.ftl", "format": "ftl"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
    ]

    # Test search with multiple parameters
    with django_assert_num_queries(7):
        response = APIClient().get(
            f"/api/v2/search/translations/?locale={locale_a.code}&project={project_a.slug}&text=the%20Test&search_match_whole_word=true&search_match_case=true",
            HTTP_ACCEPT="application/json",
        )

    assert response.status_code == 200

    assert response.data["results"] == [
        {
            "id": entities["entity_b"].id,
            "string": "the project_a Test",
            "key": ["TestKey_B_squibb"],
            "project": {"slug": "project-a", "name": "Project A"},
            "resource": {"path": "resource_project-a_1.po", "format": "gettext"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
        {
            "id": entities["entity_f"].id,
            "string": "the project_a Flibbertigibbet Test",
            "key": [],
            "project": {"slug": "project-a", "name": "Project A"},
            "resource": {"path": "resource_project-a_2.ini", "format": "ini"},
            "translation": {
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "translation_Geonosian",
            },
        },
    ]


@pytest.mark.django_db
def test_pretranslation_group_authentication(member):
    dummy_group = Group.objects.create(name="dummies")

    member.user.groups.add(dummy_group)
    token = PersonalAccessToken.objects.create(
        user=member.user,
        name="Test Token 1",
        token_hash="hashed_token",
        expires_at=now() + timedelta(days=1),
    )
    token_id = token.id
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()

    # test no pretranslators group
    response = APIClient().post(
        "/api/v2/pretranslate/",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 403
    assert response.data == {
        "detail": "You do not have permission to perform this action."
    }


@pytest.mark.django_db
def test_pretranslation_tm(member):
    pretranslators = Group.objects.get(name="pretranslators")
    member.user.groups.add(pretranslators)
    token = PersonalAccessToken.objects.create(
        user=member.user,
        name="Test Token 1",
        token_hash="hashed_token",
        expires_at=now() + timedelta(days=1),
    )
    token_id = token.id
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()

    locale_a = LocaleFactory(
        code="kg",
        name="Klingon",
    )
    project_a = ProjectFactory(
        slug="project_a",
        name="Project A",
        repositories=[],
    )
    resource_a = ResourceFactory.create(
        project=project_a,
        path=f"resource_{project_a.slug}.po",
        format="po",
    )
    entity_a = EntityFactory.create(
        string="Entity A",
        resource=resource_a,
    )
    locale_b = LocaleFactory(
        code="gs",
        name="Geonosian",
    )
    project_b = ProjectFactory(
        slug="project_b",
        name="Project B",
    )
    resource_b = ResourceFactory.create(
        project=project_b,
        path=f"resource_{project_b.slug}.ftl",
        format="fluent",
    )
    entity_b = EntityFactory.create(
        string="Entity B",
        resource=resource_b,
    )
    project_c = ProjectFactory(
        slug="project_c",
        name="Project C",
    )
    resource_c = ResourceFactory.create(
        project=project_c,
        path=f"resource_{project_c.slug}.ftl",
        format="android",
    )
    entity_c = EntityFactory.create(
        string="Entity C",
        resource=resource_c,
    )
    entity_d = EntityFactory.create(
        string="Entity D",
        resource=resource_c,
    )
    TranslationMemoryEntry.objects.create(
        source="Hello",
        target="Hola",
        locale=locale_a,
        project=project_a,
        entity=entity_a,
    )
    TranslationMemoryEntry.objects.create(
        source="{ -object-name } is a test",
        target="{ -object-name } es una prueba",
        locale=locale_a,
        project=project_b,
        entity=entity_b,
    )
    (
        TranslationMemoryEntry.objects.create(
            source="Hello",
            target="Bonjour",
            locale=locale_b,
            project=project_b,
            entity=entity_b,
        ),
    )
    (
        TranslationMemoryEntry.objects.create(
            source="The page at %1$s says:",
            target="La página en %1$s dice:",
            locale=locale_b,
            project=project_b,
            entity=entity_c,
        ),
    )
    TranslationMemoryEntry.objects.create(
        source="Your app failed validation with {0} error.",
        target="La validación de tu app ha fallado con {0} error:",
        locale=locale_b,
        project=project_c,
        entity=entity_d,
    )

    # test no locale no text
    response = APIClient().post(
        "/api/v2/pretranslate/",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 400
    assert response.data == {
        "locale": ["This field is required."],
        "text": ["This field is required."],
    }

    # test corrupted input
    corrupted_data = b"\x80\x81\x82"  # Invalid UTF-8
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=kg",
        data=corrupted_data,
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 400
    assert response.data == {
        "text": ["Unable to decode request body as UTF-8."],
    }

    # test string with spaces
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=kg",
        data="    ",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 400
    assert response.data == {
        "text": ["This field is required."],
    }

    # test empty string
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=kg",
        data="",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 400
    assert response.data == {
        "text": ["This field is required."],
    }

    # test massive character payload
    large_char_data = "a" * 2049  # payload larger than 2048 characters
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=kg",
        data=large_char_data,
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 400
    assert response.data == {
        "text": ["Text exceeds maximum length of 2048 characters."],
    }

    # test bad resource format
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=kg&resource_format=blah",
        data="Hello",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 400
    assert response.data == {
        "resource_format": ["Choose a correct resource format."],
    }

    # test no resource format
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=kg",
        data="Hello",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 200
    assert response.data == {
        "text": "Hola",
        "author": "tm",
    }

    # test fluent resource format
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=kg&resource_format=fluent",
        data="testing-alias = { -object-name } is a test",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 200
    assert response.data == {
        "text": "testing-alias = { -object-name } es una prueba\n",
        "author": "tm",
    }

    # test incorrect format on fluent
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=kg&resource_format=fluent",
        data="The page at %1$s says:",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 400

    # test android resource format
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=gs&resource_format=android",
        data="The page at %1$s says:",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 200
    assert response.data == {
        "text": "La página en %1$s dice:",
        "author": "tm",
    }

    # test incorrect format on android
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=gs&resource_format=android",
        data="testing-alias = { -object-name } is a test",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 400

    # test gettext resource format
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=gs&resource_format=gettext",
        data="Your app failed validation with {0} error.",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 200
    assert response.data == {
        "text": "La validación de tu app ha fallado con \\{0\\} error:",
        "author": "tm",
    }

    # test incorrect format on gettext
    response = APIClient().post(
        "/api/v2/pretranslate/?locale=gs&resource_format=gettext",
        data="testing-alias = { -object-name } is a test",
        content_type="text/plain",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 400
