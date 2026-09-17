from types import SimpleNamespace

import pytest

from notifications.models import Notification
from rest_framework.test import APIClient
from rest_framework.throttling import SimpleRateThrottle

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Prefetch
from django.utils.timezone import now, timedelta

from pontoon.actionlog.models import ActionLog
from pontoon.api import views
from pontoon.api.models import PersonalAccessToken
from pontoon.api.serializers import UPLOAD_KEYS_ERROR_LIMIT
from pontoon.base.models.changed_entity_locale import ChangedEntityLocale
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.resource import Resource
from pontoon.base.models.translated_resource import TranslatedResource
from pontoon.base.models.translation import Translation
from pontoon.base.models.translation_memory import TranslationMemoryEntry
from pontoon.settings.base import TERMINOLOGY_API_MAX_CHARS
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
def test_user_actions_includes_implicit_flag(member):
    from pontoon.actionlog.models import ActionLog

    client = APIClient()
    client.force_authenticate(user=member.user)

    project = ProjectFactory(slug="public-project", visibility="public")
    resource = ResourceFactory(project=project)
    entity = EntityFactory(resource=resource)
    translation = TranslationFactory(entity=entity, user=member.user)

    # Self-approval on submission: created + implicit approved.
    ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        performed_by=member.user,
        translation=translation,
    )
    ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=member.user,
        translation=translation,
        is_implicit_action=True,
    )

    date = now().strftime("%Y-%m-%d")
    response = client.get(
        f"/api/v2/user-actions/{date}/project/{project.slug}/",
        HTTP_ACCEPT="application/json",
    )

    assert response.status_code == 200
    actions = response.data["actions"]
    flags = {action["type"]: action["is_implicit_action"] for action in actions}
    assert flags == {
        "translation:created": False,
        "translation:approved": True,
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
    translated_resource.approved_strings = 10
    translated_resource.pretranslated_strings = 5
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
        "script": "Latn",
        "script_name": "Latin",
        "google_translate_code": "",
        "ms_terminology_code": "",
        "ms_translator_code": "",
        "team_description": "",
        "total_strings": 25,
        "approved_strings": 10,
        "pretranslated_strings": 5,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "completed_strings": 12,
        "complete": False,
        "projects": ["terminology"],
    }

    assert {
        "project": {
            "slug": "terminology",
            "name": "Terminology",
        },
        "total_strings": 25,
        "approved_strings": 10,
        "pretranslated_strings": 5,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "completed_strings": 12,
        "complete": False,
    } in localizations


@pytest.mark.django_db
def test_locale_renamed_code_redirects():
    """Requesting a locale by its old code redirects to the new code."""
    locale = Locale.objects.get(code="af")
    locale.code = "af-renamed"
    locale.save()

    response = APIClient().get("/api/v2/locales/af/", HTTP_ACCEPT="application/json")

    assert response.status_code == 302
    assert response["Location"] == "/api/v2/locales/af-renamed/"


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
        translated_resource.approved_strings = 10
        translated_resource.pretranslated_strings = 5
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
            "script_name": loc.get_script_display(),
            "google_translate_code": loc.google_translate_code,
            "ms_terminology_code": loc.ms_terminology_code,
            "ms_translator_code": loc.ms_translator_code,
            "team_description": loc.team_description,
            "total_strings": loc.total_strings,
            "approved_strings": loc.approved_strings,
            "pretranslated_strings": loc.pretranslated_strings,
            "strings_with_warnings": loc.strings_with_warnings,
            "strings_with_errors": loc.strings_with_errors,
            "missing_strings": loc.missing_strings,
            "unreviewed_strings": loc.unreviewed_strings,
            "completed_strings": loc.completed_strings,
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
        translated_resource.approved_strings = 10
        translated_resource.pretranslated_strings = 5
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
        "approved_strings": 20,
        "pretranslated_strings": 10,
        "strings_with_warnings": 4,
        "strings_with_errors": 6,
        "missing_strings": 10,
        "unreviewed_strings": 10,
        "completed_strings": 24,
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
        "approved_strings": 10,
        "pretranslated_strings": 5,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "completed_strings": 12,
        "complete": False,
    } in localizations

    assert {
        "locale": {
            "code": "af",
            "name": "Afrikaans",
        },
        "total_strings": 25,
        "approved_strings": 10,
        "pretranslated_strings": 5,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "completed_strings": 12,
        "complete": False,
    } in localizations


@pytest.mark.django_db
def test_project_locale_renamed_redirects():
    """Requesting a project locale by an old code and old slug redirects to the new URL."""
    locale = Locale.objects.get(code="af")
    locale.code = "af-renamed"
    locale.save()
    project = Project.objects.get(slug="terminology")
    project.slug = "terminology-renamed"
    project.save()

    response = APIClient().get(
        "/api/v2/af/terminology/", HTTP_ACCEPT="application/json"
    )

    assert response.status_code == 302
    assert response["Location"] == "/api/v2/af-renamed/terminology-renamed/"


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
    # 1 project lookup + 1 ProjectSlugHistory fallback lookup on the 404 path
    with django_assert_num_queries(2):
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
    ] + [
        ResourceFactory.create(
            project=project_1, path="resource_a_2.po", format="gettext"
        )
    ]

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
        translated_resource.approved_strings = 10
        translated_resource.pretranslated_strings = 5
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
            "completed_strings": p.completed_strings,
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
            "completed_strings": p.completed_strings,
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
            "completed_strings": p.completed_strings,
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
def test_project_visibility(django_assert_num_queries, client_superuser):
    ProjectFactory.create_batch(3, disabled=True, visibility="public")
    ProjectFactory.create_batch(3, disabled=True, visibility="private")
    ProjectFactory.create_batch(3, system_project=True, visibility="public")
    ProjectFactory.create_batch(3, system_project=True, visibility="private")

    url = "/api/v2/projects/?fields=slug,visibility&include_disabled=true&include_system=true"

    # public API usage
    with django_assert_num_queries(2):
        response = APIClient().get(url)

        assert response.status_code == 200

    # 8 projects includes Tutorial & Terminology
    assert response.data["count"] == 8
    for res in response.data["results"]:
        assert res["visibility"] == "public"

    # admin API usage
    with django_assert_num_queries(4):
        response = client_superuser.get(url)

        assert response.status_code == 200

    # 14 projects includes Tutorial & Terminology
    assert response.data["count"] == 14


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
                "locale": {"code": "gs", "name": "Geonosian"},
                "string": "approved_translation_Geonosian",
            },
            {
                "locale": {"code": "hut", "name": "Huttese"},
                "string": "approved_translation_Huttese",
            },
            {
                "locale": {"code": "kg", "name": "Klingon"},
                "string": "approved_translation_Klingon",
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
        translated_resource.approved_strings = 10
        translated_resource.pretranslated_strings = 5
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
            "script": "Latn",
            "script_name": "Latin",
            "google_translate_code": "af",
            "ms_terminology_code": "af-za",
            "ms_translator_code": "af",
            "team_description": "",
            "total_strings": 25,
            "approved_strings": 10,
            "pretranslated_strings": 5,
            "strings_with_warnings": 2,
            "strings_with_errors": 3,
            "missing_strings": 5,
            "unreviewed_strings": 5,
            "completed_strings": 12,
            "complete": False,
        },
        "total_strings": 25,
        "approved_strings": 10,
        "pretranslated_strings": 5,
        "strings_with_warnings": 2,
        "strings_with_errors": 3,
        "missing_strings": 5,
        "unreviewed_strings": 5,
        "completed_strings": 12,
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
            "approved_strings": 20,
            "pretranslated_strings": 10,
            "strings_with_warnings": 4,
            "strings_with_errors": 6,
            "missing_strings": 10,
            "unreviewed_strings": 10,
            "completed_strings": 24,
            "complete": False,
        },
    }


@pytest.mark.django_db
def test_project_renamed_slug_redirects():
    """Requesting a project by its old slug redirects to the new slug."""
    project = Project.objects.get(slug="terminology")
    project.slug = "terminology-renamed"
    project.save()

    response = APIClient().get(
        "/api/v2/projects/terminology/", HTTP_ACCEPT="application/json"
    )

    assert response.status_code == 302
    assert response["Location"] == "/api/v2/projects/terminology-renamed/"


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


@pytest.fixture
def terminology_matches_setup():
    locale = LocaleFactory(code="kg", name="Klingon")
    other_locale = LocaleFactory(code="gs", name="Geonosian")

    term_open = Term.objects.create(
        text="open",
        part_of_speech="verb",
        definition="Allow access",
        usage="Open the door.",
    )
    term_tab = Term.objects.create(
        text="tab",
        part_of_speech="noun",
        definition="A page in the browser",
        usage="Open a new tab.",
    )
    term_click = Term.objects.create(
        text="click",
        part_of_speech="verb",
        definition="Press",
        usage="Click the button.",
    )
    Term.objects.create(
        text="Firefox",
        part_of_speech="noun",
        definition="A web browser",
        do_not_translate=True,
    )
    # Terms without a definition, or forbidden, are never matched
    Term.objects.create(text="window", part_of_speech="noun", definition="")
    Term.objects.create(
        text="bookmark",
        part_of_speech="noun",
        definition="A saved page",
        forbidden=True,
    )

    TermTranslation.objects.create(term=term_open, locale=locale, text="odpri")
    TermTranslation.objects.create(term=term_tab, locale=locale, text="zavihek")
    TermTranslation.objects.create(term=term_click, locale=other_locale, text="klikni")

    return SimpleNamespace(locale=locale, other_locale=other_locale)


@pytest.mark.django_db
def test_terminology_matches(terminology_matches_setup, django_assert_num_queries):
    with django_assert_num_queries(3):
        response = APIClient().get(
            "/api/v2/terminology/matches/",
            {"locale": "kg", "text": "Open a new tab in this window."},
        )

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
                "translation_text": "odpri",
                "usage": "Open the door.",
                "notes": "",
            },
            {
                "definition": "A page in the browser",
                "part_of_speech": "noun",
                "text": "tab",
                "translation_text": "zavihek",
                "usage": "Open a new tab.",
                "notes": "",
            },
        ],
    }


@pytest.mark.django_db
def test_terminology_matches_word_start(terminology_matches_setup):
    """Terms are matched at the start of a word, to also catch inflected forms."""
    response = APIClient().get(
        "/api/v2/terminology/matches/",
        {"locale": "kg", "text": "Reopened the crab."},
    )

    assert response.status_code == 200
    assert response.data["results"] == []

    response = APIClient().get(
        "/api/v2/terminology/matches/",
        {"locale": "kg", "text": "Opened the tabs."},
    )

    assert response.status_code == 200
    assert [t["text"] for t in response.data["results"]] == ["open", "tab"]


@pytest.mark.django_db
def test_terminology_matches_missing_translation(
    terminology_matches_setup,
):
    response = APIClient().get(
        "/api/v2/terminology/matches/",
        {"locale": "kg", "text": "Click here."},
    )

    assert response.status_code == 200
    assert [(t["text"], t["translation_text"]) for t in response.data["results"]] == [
        ("click", None)
    ]


@pytest.mark.django_db
def test_terminology_matches_do_not_translate(terminology_matches_setup):
    """Terms that must not be translated are reported as-is, in every locale."""
    response = APIClient().get(
        "/api/v2/terminology/matches/",
        {"locale": "kg", "text": "Open Firefox."},
    )

    assert response.status_code == 200
    assert [(t["text"], t["translation_text"]) for t in response.data["results"]] == [
        ("Firefox", "Firefox"),
        ("open", "odpri"),
    ]


@pytest.mark.django_db
def test_terminology_matches_fields(terminology_matches_setup):
    response = APIClient().get(
        "/api/v2/terminology/matches/",
        {"locale": "kg", "text": "Open a new tab.", "fields": "text"},
    )

    assert response.status_code == 200
    assert response.data["results"] == [{"text": "open"}, {"text": "tab"}]


@pytest.mark.django_db
def test_terminology_matches_errors(terminology_matches_setup):
    client = APIClient()

    response = client.get("/api/v2/terminology/matches/", {"text": "Open"})
    assert response.status_code == 400
    assert response.data == {"locale": ["This field is required."]}

    response = client.get("/api/v2/terminology/matches/", {"locale": "kg"})
    assert response.status_code == 400
    assert response.data == {"text": ["This field is required."]}

    response = client.get(
        "/api/v2/terminology/matches/", {"locale": "missing", "text": "Open"}
    )
    assert response.status_code == 404

    response = client.get(
        "/api/v2/terminology/matches/",
        {"locale": "kg", "text": "Open a new tab. " * TERMINOLOGY_API_MAX_CHARS},
    )
    assert response.status_code == 400
    assert response.data == {
        "text": [
            f"Text exceeds maximum length of {TERMINOLOGY_API_MAX_CHARS} characters."
        ]
    }

    # Whitespace-only text that is also too long reports the length error
    response = client.get(
        "/api/v2/terminology/matches/",
        {"locale": "kg", "text": " " * (TERMINOLOGY_API_MAX_CHARS + 1)},
    )
    assert response.status_code == 400
    assert response.data == {
        "text": [
            f"Text exceeds maximum length of {TERMINOLOGY_API_MAX_CHARS} characters."
        ]
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "rates",
    [
        {"terminology_burst": "2/minute", "terminology_sustained": "1000/hour"},
        {"terminology_burst": "60/minute", "terminology_sustained": "2/hour"},
    ],
)
def test_terminology_matches_throttled(monkeypatch, terminology_matches_setup, rates):
    # DRF copies the rates into a class attribute at import time, so overriding the
    # REST_FRAMEWORK setting has no effect here.
    monkeypatch.setattr(SimpleRateThrottle, "THROTTLE_RATES", rates)
    cache.clear()

    client = APIClient()
    for expected_status in (200, 200, 429):
        response = client.get(
            "/api/v2/terminology/matches/", {"locale": "kg", "text": "Open a new tab."}
        )
        assert response.status_code == expected_status

    cache.clear()


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
def test_entity_search(django_assert_num_queries):
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
        string="entity-b = Entity B\n",
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


@pytest.mark.django_db
def test_pat_auth_on_locales_endpoint(member):
    """PAT authentication works on non-pretranslation endpoints."""
    token = PersonalAccessToken.objects.create(
        user=member.user,
        name="Test Token PAT Locales",
        token_hash="hashed_token",
        expires_at=now() + timedelta(days=1),
    )
    token_id = token.id
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()

    response = APIClient().get(
        "/api/v2/locales/",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_session_auth_still_works_on_user_actions(member):
    """Session authentication continues to work after PAT auth is added to defaults."""
    client = APIClient()
    client.force_authenticate(user=member.user)

    project = ProjectFactory(slug="test-session-project")
    date = now().strftime("%Y-%m-%d")

    response = client.get(
        f"/api/v2/user-actions/{date}/project/{project.slug}/",
        HTTP_ACCEPT="application/json",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_expired_pat_rejected_on_non_pretranslation_endpoint(member):
    """Expired PAT returns 403 on non-pretranslation endpoints."""
    token = PersonalAccessToken.objects.create(
        user=member.user,
        name="Test Token Expired",
        token_hash="hashed_token",
        expires_at=now() - timedelta(days=1),
    )
    token_id = token.id
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()

    response = APIClient().get(
        "/api/v2/locales/",
        HTTP_ACCEPT="application/json",
        headers={"Authorization": f"Bearer {token_id}_{token_unhashed}"},
    )

    assert response.status_code == 403


def _pat_client(user, name="Upload Token"):
    token = PersonalAccessToken.objects.create(
        user=user,
        name=name,
        token_hash="placeholder",
        expires_at=now() + timedelta(days=1),
    )
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.id}_{token_unhashed}")
    return client


def _upload(client, **data):
    return client.post("/api/v2/upload/translations/", data, format="multipart")


def _po_file(
    contents='msgid "test_key"\nmsgstr "new translation"', name="resource_a.po"
):
    return SimpleUploadedFile(name, contents.encode("utf-8"))


@pytest.fixture
def upload_translator(member, project_locale_a):
    project_locale_a.locale.translators_group.user_set.add(member.user)
    return member


@pytest.fixture
def upload_po_translation(translation_a):
    translation_a.entity.key = ["test_key"]
    translation_a.entity.save()
    return translation_a


@pytest.mark.django_db
def test_upload_api_requires_authentication(project_locale_a):
    response = _upload(
        APIClient(),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource="resource_a.po",
        uploadfile=_po_file(),
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_api_session_auth_rejected(upload_translator, project_locale_a):
    client = APIClient()
    # force_authenticate() would bypass authentication_classes.
    client.force_login(upload_translator.user)

    response = _upload(
        client,
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource="resource_a.po",
        uploadfile=_po_file(),
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_api_cannot_translate(member, project_locale_a, resource_a):
    response = _upload(
        _pat_client(member.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource="resource_a.po",
        uploadfile=_po_file(),
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_api_readonly_project_locale(
    upload_translator, project_locale_a, resource_a
):
    project_locale_a.readonly = True
    project_locale_a.save()

    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource="resource_a.po",
        uploadfile=_po_file(),
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_api_missing_file(upload_translator, project_locale_a):
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource="resource_a.po",
    )

    assert response.status_code == 400
    assert "uploadfile" in response.json()


@pytest.mark.django_db
def test_upload_api_missing_project(upload_translator, project_locale_a):
    response = _upload(
        _pat_client(upload_translator.user),
        locale=project_locale_a.locale.code,
        resource="resource_a.po",
        uploadfile=_po_file(),
    )

    assert response.status_code == 400
    assert "project" in response.json()


@pytest.mark.django_db
def test_upload_api_incompatible_format(
    upload_translator, project_locale_a, upload_po_translation
):
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(contents="irrelevant", name="resource_a.ftl"),
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_upload_api_unparseable_file(
    upload_translator, project_locale_a, upload_po_translation
):
    """Reject malformed files."""
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(contents="this is not valid gettext {{{ broken"),
    )

    assert response.status_code == 400
    assert "uploadfile" in response.json()


@pytest.mark.django_db
def test_upload_api_unknown_keys_ignored(
    upload_translator, project_locale_a, upload_po_translation
):
    """Skip unknown keys and report them, importing the rest of the file."""
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(
            contents='msgid "test_key"\nmsgstr "new translation"\n\n'
            'msgid "no_such_key"\nmsgstr "x"\n\n'
            'msgid "another_missing"\nmsgstr "y"\n'
        ),
    )

    assert response.status_code == 200
    assert response.json() == {
        "updated": 1,
        "unchanged": 0,
        "undefined_keys": [["no_such_key"], ["another_missing"]],
        "undefined_keys_count": 2,
    }
    assert Translation.objects.filter(string="new translation").exists()


@pytest.mark.django_db
def test_upload_api_unknown_keys_truncated(
    upload_translator, project_locale_a, upload_po_translation
):
    """Report at most UPLOAD_KEYS_ERROR_LIMIT unknown keys, alongside their total number."""
    unknown = 2 * UPLOAD_KEYS_ERROR_LIMIT
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(
            contents="\n\n".join(
                f'msgid "missing_{i}"\nmsgstr "x"' for i in range(unknown)
            )
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["undefined_keys"]) == UPLOAD_KEYS_ERROR_LIMIT
    assert body["undefined_keys_count"] == unknown


@pytest.mark.django_db
def test_upload_api_badge_notification(
    monkeypatch, upload_translator, project_locale_a, upload_po_translation
):
    """Crossing a badge threshold through the API notifies the user."""
    levels = iter([0, 1])
    monkeypatch.setattr(views, "badges_translation_level", lambda user: next(levels))
    monkeypatch.setattr(views, "badges_review_level", lambda user: 0)

    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(),
    )

    assert response.status_code == 200
    notification = Notification.objects.filter(
        recipient=upload_translator.user, data__category="badge"
    ).get()
    assert "Translation Champion" in notification.description


@pytest.mark.django_db
def test_upload_api_no_badge_notification_below_threshold(
    monkeypatch, upload_translator, project_locale_a, upload_po_translation
):
    """No notification when the upload doesn't move the user to a new badge level."""
    monkeypatch.setattr(views, "badges_translation_level", lambda user: 1)
    monkeypatch.setattr(views, "badges_review_level", lambda user: 0)

    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(),
    )

    assert response.status_code == 200
    assert not Notification.objects.filter(
        recipient=upload_translator.user, data__category="badge"
    ).exists()


@pytest.mark.django_db
def test_upload_api_file_without_translations(
    upload_translator, project_locale_a, upload_po_translation
):
    """Reject files with no translations, rather than reporting a no-op."""
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(contents="# Just a comment\n"),
    )

    assert response.status_code == 400
    assert response.json() == {
        "uploadfile": ["No translations found in uploaded file."]
    }


@pytest.mark.django_db
def test_upload_api_disabled_project(
    upload_translator, project_locale_a, upload_po_translation
):
    """Reject disabled projects."""
    project = project_locale_a.project
    project.disabled = True
    project.save()

    response = _upload(
        _pat_client(upload_translator.user),
        project=project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(contents='msgid "test_key"\nmsgstr "into disabled"'),
    )

    assert response.status_code == 404
    assert not Translation.objects.filter(string="into disabled").exists()


@pytest.mark.django_db
def test_upload_api_oversized_file(
    upload_translator, project_locale_a, upload_po_translation
):
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(contents="#" * (5000 * 1000 + 1)),
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_upload_api_file_validated_after_authorization(
    member, project_locale_a, resource_a
):
    """An oversized file from a user without translator rights is a 403, not a 400."""
    response = _upload(
        _pat_client(member.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=resource_a.path,
        uploadfile=_po_file(contents="#" * (5000 * 1000 + 1)),
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_api_resource_not_enabled_for_locale(
    upload_translator, project_locale_a, resource_a
):
    """A resource with no TranslatedResource for the locale is not writable."""
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=resource_a.path,
        uploadfile=_po_file(),
    )

    assert response.status_code == 404
    assert not Translation.objects.filter(entity__resource=resource_a).exists()


@pytest.mark.django_db
def test_upload_api_concurrent_conflict(
    monkeypatch, upload_translator, project_locale_a, upload_po_translation
):
    """A uniqueness clash with a concurrent upload is reported as a conflict."""
    from django.db import IntegrityError

    from pontoon.sync import upload as sync_upload

    def raise_integrity_error(*args, **kwargs):
        raise IntegrityError("duplicate key value violates unique constraint")

    monkeypatch.setattr(sync_upload, "import_uploaded_file", raise_integrity_error)

    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(),
    )

    assert response.status_code == 409


@pytest.mark.django_db
def test_upload_api_unknown_resource(upload_translator, project_locale_a):
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource="does_not_exist.po",
        uploadfile=_po_file(name="does_not_exist.po"),
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_api_locale_not_enabled_for_project(member, project_locale_a, locale_b):
    locale_b.translators_group.user_set.add(member.user)

    response = _upload(
        _pat_client(member.user),
        project=project_locale_a.project.slug,
        locale=locale_b.code,
        resource="resource_a.po",
        uploadfile=_po_file(),
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_api_admin_can_upload(member, project_locale_a, upload_po_translation):
    member.user.is_superuser = True
    member.user.save()

    assert not project_locale_a.locale.translators_group.user_set.filter(
        pk=member.user.pk
    ).exists()

    response = _upload(
        _pat_client(member.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(),
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 1


@pytest.mark.django_db
def test_upload_api_unknown_locale(upload_translator, project_locale_a):
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale="does-not-exist",
        resource="resource_a.po",
        uploadfile=_po_file(),
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_api_private_project_not_visible(
    upload_translator, project_locale_a, upload_po_translation
):
    project = project_locale_a.project
    project.visibility = Project.Visibility.PRIVATE
    project.save()

    response = _upload(
        _pat_client(upload_translator.user),
        project=project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(),
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_api_file(upload_translator, project_locale_a, upload_po_translation):
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "updated": 1,
        "unchanged": 0,
        "undefined_keys": [],
        "undefined_keys_count": 0,
    }

    translation = Translation.objects.get(string="new translation")

    assert translation.entity.key == ["test_key"]
    assert translation.entity.resource.path == "resource_a.po"
    assert translation.approved
    assert translation.user == upload_translator.user
    assert not translation.warnings.exists()


@pytest.mark.django_db
def test_upload_api_no_changes(
    upload_translator, project_locale_a, upload_po_translation
):
    client = _pat_client(upload_translator.user)
    kwargs = dict(
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
    )

    first = _upload(client, uploadfile=_po_file(), **kwargs)
    assert first.status_code == 200
    assert first.json()["updated"] == 1

    second = _upload(client, uploadfile=_po_file(), **kwargs)
    assert second.status_code == 200
    assert second.json() == {
        "updated": 0,
        "unchanged": 1,
        "undefined_keys": [],
        "undefined_keys_count": 0,
    }


@pytest.mark.django_db
def test_upload_api_logs_action(
    upload_translator, project_locale_a, upload_po_translation
):
    response = _upload(
        _pat_client(upload_translator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=upload_po_translation.entity.resource.path,
        uploadfile=_po_file(),
    )

    assert response.status_code == 200
    assert ActionLog.objects.filter(
        performed_by=upload_translator.user,
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "rates",
    [
        {"upload_burst": "2/minute", "upload_sustained": "1000/hour"},
        {"upload_burst": "60/minute", "upload_sustained": "2/hour"},
    ],
)
def test_upload_api_throttled(
    monkeypatch, upload_translator, project_locale_a, upload_po_translation, rates
):
    # DRF copies the rates into a class attribute at import time, so overriding the
    # REST_FRAMEWORK setting has no effect here.
    monkeypatch.setattr(SimpleRateThrottle, "THROTTLE_RATES", rates)
    cache.clear()

    client = _pat_client(upload_translator.user)
    for expected_status in (200, 200, 429):
        response = _upload(
            client,
            project=project_locale_a.project.slug,
            locale=project_locale_a.locale.code,
            resource=upload_po_translation.entity.resource.path,
            uploadfile=_po_file(),
        )
        assert response.status_code == expected_status

    cache.clear()


def _upload_pretranslations(client, **data):
    return client.post("/api/v2/upload/pretranslations/", data, format="multipart")


@pytest.fixture
def pretranslator(upload_translator):
    upload_translator.user.groups.add(Group.objects.get(name="pretranslators"))
    return upload_translator


@pytest.fixture
def untranslated_entity(upload_po_translation):
    """An entity without translations, in the same resource as `upload_po_translation`."""
    return EntityFactory.create(
        resource=upload_po_translation.entity.resource,
        string="Other entity",
        key=["other_key"],
    )


def _upload_pretranslation(client, project_locale, resource_path, contents=None):
    kwargs = {"contents": contents} if contents is not None else {}
    return _upload_pretranslations(
        client,
        project=project_locale.project.slug,
        locale=project_locale.locale.code,
        resource=resource_path,
        uploadfile=_po_file(**kwargs),
    )


@pytest.mark.django_db
def test_upload_pretranslations_requires_authentication(
    project_locale_a, upload_po_translation
):
    response = _upload_pretranslation(
        APIClient(), project_locale_a, upload_po_translation.entity.resource.path
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_pretranslations_requires_pretranslators_group(
    upload_translator, project_locale_a, upload_po_translation
):
    """Translator rights alone are not enough."""
    response = _upload_pretranslation(
        _pat_client(upload_translator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 403
    assert not Translation.objects.filter(pretranslated=True).exists()


@pytest.mark.django_db
def test_upload_pretranslations_requires_translate_permission(
    member, project_locale_a, upload_po_translation
):
    """Membership of the pretranslators group alone is not enough."""
    member.user.groups.add(Group.objects.get(name="pretranslators"))

    response = _upload_pretranslation(
        _pat_client(member.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 403
    assert not Translation.objects.filter(pretranslated=True).exists()


@pytest.mark.django_db
def test_upload_pretranslations_readonly_project_locale(
    pretranslator, project_locale_a, upload_po_translation
):
    project_locale_a.readonly = True
    project_locale_a.save()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_pretranslations_creates_pretranslation(
    pretranslator, project_locale_a, untranslated_entity
):
    """An untranslated string gets a new pretranslation, authored by the PAT user."""
    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        untranslated_entity.resource.path,
        contents='msgid "other_key"\nmsgstr "pretranslation"',
    )

    assert response.status_code == 200
    assert response.json() == {
        "created": 1,
        "replaced": 0,
        "converted": 0,
        "unchanged": 0,
        "skipped": 0,
        "failed_checks": [],
        "failed_checks_count": 0,
        "undefined_keys": [],
        "undefined_keys_count": 0,
    }

    translation = Translation.objects.get(entity=untranslated_entity)

    assert translation.string == "pretranslation"
    assert translation.pretranslated
    assert translation.active
    assert not translation.approved
    assert translation.user == pretranslator.user
    assert ActionLog.objects.filter(
        performed_by=pretranslator.user,
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation,
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_skips_fuzzy_uploads(
    pretranslator, project_locale_a, untranslated_entity
):
    """A translation marked as fuzzy in the file is not stored as a pretranslation."""
    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        untranslated_entity.resource.path,
        contents='#, fuzzy\nmsgid "other_key"\nmsgstr "pretranslation"',
    )

    assert response.status_code == 200
    assert response.json() == {
        "created": 0,
        "replaced": 0,
        "converted": 0,
        "unchanged": 0,
        "skipped": 1,
        "failed_checks": [],
        "failed_checks_count": 0,
        "undefined_keys": [],
        "undefined_keys_count": 0,
    }
    assert not Translation.objects.filter(entity=untranslated_entity).exists()


@pytest.mark.django_db
def test_upload_pretranslations_fuzzy_upload_keeps_existing_pretranslation(
    pretranslator, project_locale_a, upload_po_translation
):
    """A fuzzy entry leaves a different, existing pretranslation in place."""
    upload_po_translation.approved = False
    upload_po_translation.pretranslated = True
    upload_po_translation.active = True
    upload_po_translation.save()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
        contents='#, fuzzy\nmsgid "test_key"\nmsgstr "fuzzy translation"',
    )

    assert response.status_code == 200
    assert response.json()["skipped"] == 1

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.pretranslated
    assert not upload_po_translation.rejected
    assert upload_po_translation.active
    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_drops_replacement_with_errors(
    monkeypatch, pretranslator, project_locale_a, upload_po_translation
):
    """A replacement that fails checks is not stored, keeping the previous translation."""
    from pontoon.sync import upload as sync_upload

    def failing_checks(entity, locale_code, string, use_tt_checks):
        return (
            {"pErrors": ["Test error", "Other error"]}
            if string == "new translation"
            else {}
        )

    monkeypatch.setattr(sync_upload, "run_checks", failing_checks)

    upload_po_translation.pretranslated = True
    upload_po_translation.active = True
    upload_po_translation.save()
    ChangedEntityLocale.objects.all().delete()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["replaced"] == 0
    assert response.json()["failed_checks"] == [
        {"key": ["test_key"], "errors": ["Test error", "Other error"], "warnings": []}
    ]
    assert response.json()["failed_checks_count"] == 1
    assert not Translation.objects.filter(string="new translation").exists()

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.pretranslated
    assert upload_po_translation.active
    assert not upload_po_translation.rejected
    assert not ChangedEntityLocale.objects.filter(
        entity=upload_po_translation.entity
    ).exists()
    assert not ActionLog.objects.filter(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        performed_by=pretranslator.user,
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_keeps_matching_fuzzy_with_warnings(
    monkeypatch, pretranslator, project_locale_a, upload_po_translation
):
    """A matching fuzzy translation with warnings stays fuzzy and exported as it is."""
    from pontoon.sync import upload as sync_upload

    def failing_checks(entity, locale_code, string, use_tt_checks):
        return {"pndbWarnings": ["Test warning"]} if string == "new translation" else {}

    monkeypatch.setattr(sync_upload, "run_checks", failing_checks)

    upload_po_translation.fuzzy = True
    upload_po_translation.active = True
    upload_po_translation.string = "new translation"
    upload_po_translation.value = ["new translation"]
    upload_po_translation.save()
    ChangedEntityLocale.objects.all().delete()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["converted"] == 0
    assert response.json()["failed_checks_count"] == 1

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.fuzzy
    assert not upload_po_translation.pretranslated
    assert not ChangedEntityLocale.objects.filter(
        entity=upload_po_translation.entity
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_reports_missing_placeholder(
    pretranslator, project_locale_a
):
    """A dropped placeholder is caught, though it is not a check stored in the DB."""
    resource = ResourceFactory.create(
        project=project_locale_a.project,
        path="values/strings.xml",
        format=Resource.Format.ANDROID,
    )
    TranslatedResourceFactory.create(resource=resource, locale=project_locale_a.locale)
    EntityFactory.create(
        resource=resource, string="The page at {$arg1} says:", key=["page_at"]
    )

    response = _upload_pretranslations(
        _pat_client(pretranslator.user),
        project=project_locale_a.project.slug,
        locale=project_locale_a.locale.code,
        resource=resource.path,
        uploadfile=SimpleUploadedFile(
            "strings.xml",
            b'<?xml version="1.0" encoding="utf-8"?>\n'
            b"<resources>\n"
            b'  <string name="page_at">La pagina sul server riporta:</string>\n'
            b"</resources>\n",
        ),
    )

    assert response.status_code == 200
    assert response.json()["created"] == 0
    assert response.json()["failed_checks"] == [
        {
            "key": ["page_at"],
            "errors": [],
            "warnings": ["Placeholder {$arg1} not found in translation"],
        }
    ]
    assert not Translation.objects.filter(entity__resource=resource).exists()


@pytest.mark.django_db
def test_upload_pretranslations_skips_matching_translation_with_errors(
    monkeypatch, pretranslator, project_locale_a, upload_po_translation
):
    """A matching translation that fails checks is not converted, and is not deleted."""
    from pontoon.sync import upload as sync_upload

    def failing_checks(entity, locale_code, string, use_tt_checks):
        return {"pErrors": ["Test error"]} if string == "new translation" else {}

    monkeypatch.setattr(sync_upload, "run_checks", failing_checks)

    upload_po_translation.fuzzy = True
    upload_po_translation.active = True
    upload_po_translation.string = "new translation"
    upload_po_translation.value = ["new translation"]
    upload_po_translation.save()
    ChangedEntityLocale.objects.all().delete()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["converted"] == 0
    assert response.json()["failed_checks"] == [
        {"key": ["test_key"], "errors": ["Test error"], "warnings": []}
    ]
    assert response.json()["failed_checks_count"] == 1

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.fuzzy
    assert not upload_po_translation.pretranslated
    assert not upload_po_translation.rejected
    assert upload_po_translation.active
    assert not ChangedEntityLocale.objects.filter(
        entity=upload_po_translation.entity
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_updates_stats_and_marks_changed(
    pretranslator, project_locale_a, untranslated_entity
):
    """Stored pretranslations are counted in stats, and synced by the next sync."""
    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        untranslated_entity.resource.path,
        contents='msgid "other_key"\nmsgstr "pretranslation"',
    )

    assert response.status_code == 200
    assert (
        TranslatedResource.objects.get(
            resource=untranslated_entity.resource, locale=project_locale_a.locale
        ).pretranslated_strings
        == 1
    )
    assert ChangedEntityLocale.objects.filter(
        entity=untranslated_entity, locale=project_locale_a.locale
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_drops_replacement_with_warnings(
    monkeypatch, pretranslator, project_locale_a, upload_po_translation
):
    """Warnings keep a pretranslation from being exported, so it is not stored either."""
    from pontoon.sync import upload as sync_upload

    def failing_checks(entity, locale_code, string, use_tt_checks):
        return {"pndbWarnings": ["Test warning"]} if string == "new translation" else {}

    monkeypatch.setattr(sync_upload, "run_checks", failing_checks)

    upload_po_translation.pretranslated = True
    upload_po_translation.active = True
    upload_po_translation.save()
    ChangedEntityLocale.objects.all().delete()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["replaced"] == 0
    assert response.json()["failed_checks"] == [
        {"key": ["test_key"], "errors": [], "warnings": ["Test warning"]}
    ]
    assert not Translation.objects.filter(string="new translation").exists()

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.pretranslated
    assert upload_po_translation.active
    assert not upload_po_translation.rejected
    assert not ChangedEntityLocale.objects.filter(
        entity=upload_po_translation.entity
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_updates_latest_translation(
    pretranslator, project_locale_a, untranslated_entity
):
    """Latest activity is updated, as it would be by Translation.save()."""
    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        untranslated_entity.resource.path,
        contents='msgid "other_key"\nmsgstr "pretranslation"',
    )

    assert response.status_code == 200

    pretranslation = Translation.objects.get(entity=untranslated_entity)
    project_locale_a.refresh_from_db()

    assert (
        TranslatedResource.objects.get(
            resource=untranslated_entity.resource, locale=project_locale_a.locale
        ).latest_translation
        == pretranslation
    )
    assert project_locale_a.latest_translation == pretranslation


@pytest.mark.django_db
def test_upload_pretranslations_skips_approved(
    pretranslator, project_locale_a, upload_po_translation
):
    """A string with an approved translation is left untouched."""
    upload_po_translation.approved = True
    upload_po_translation.active = True
    upload_po_translation.save()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["skipped"] == 1
    assert response.json()["created"] == 0

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.approved
    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_replaces_fuzzy(
    pretranslator, project_locale_a, upload_po_translation
):
    """A different fuzzy translation is rejected and replaced."""
    upload_po_translation.fuzzy = True
    upload_po_translation.active = True
    upload_po_translation.save()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["replaced"] == 1
    assert response.json()["skipped"] == 0

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.rejected
    assert not upload_po_translation.fuzzy
    assert not upload_po_translation.active

    new_translation = Translation.objects.get(string="new translation")

    assert new_translation.pretranslated
    assert new_translation.active
    assert not new_translation.fuzzy


@pytest.mark.django_db
def test_upload_pretranslations_converts_matching_fuzzy(
    pretranslator, project_locale_a, upload_po_translation
):
    """A fuzzy translation matching the upload becomes a pretranslation."""
    author = upload_po_translation.user
    upload_po_translation.fuzzy = True
    upload_po_translation.active = True
    upload_po_translation.string = "new translation"
    upload_po_translation.value = ["new translation"]
    upload_po_translation.save()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["converted"] == 1
    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.pretranslated
    assert upload_po_translation.active
    assert not upload_po_translation.fuzzy
    assert not upload_po_translation.rejected
    assert upload_po_translation.user == author


@pytest.mark.django_db
def test_upload_pretranslations_replaces_pretranslation(
    pretranslator, project_locale_a, upload_po_translation
):
    """A different pretranslation is rejected and replaced."""
    upload_po_translation.pretranslated = True
    upload_po_translation.active = True
    upload_po_translation.save()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["replaced"] == 1
    assert response.json()["created"] == 0

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.rejected
    assert not upload_po_translation.pretranslated
    assert not upload_po_translation.active
    assert upload_po_translation.rejected_user == pretranslator.user

    new_translation = Translation.objects.get(string="new translation")

    assert new_translation.pretranslated
    assert new_translation.active
    assert ActionLog.objects.filter(
        performed_by=pretranslator.user,
        action_type=ActionLog.ActionType.TRANSLATION_REJECTED,
        translation=upload_po_translation,
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_reactivates_matching_pretranslation(
    pretranslator, project_locale_a, upload_po_translation
):
    """A matching pretranslation left inactive by a later suggestion is activated."""
    upload_po_translation.approved = False
    upload_po_translation.pretranslated = True
    upload_po_translation.active = False
    upload_po_translation.string = "new translation"
    upload_po_translation.value = ["new translation"]
    upload_po_translation.save()
    suggestion = TranslationFactory.create(
        entity=upload_po_translation.entity,
        locale=project_locale_a.locale,
        string="a suggestion",
        value=["a suggestion"],
        active=True,
    )

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["unchanged"] == 0
    assert response.json()["converted"] == 1

    upload_po_translation.refresh_from_db()
    suggestion.refresh_from_db()

    assert upload_po_translation.pretranslated
    assert upload_po_translation.active
    assert not suggestion.active
    assert not suggestion.rejected


@pytest.mark.django_db
def test_upload_pretranslations_unchanged(
    pretranslator, project_locale_a, upload_po_translation
):
    """An identical pretranslation is reported as unchanged."""
    upload_po_translation.pretranslated = True
    upload_po_translation.active = True
    upload_po_translation.string = "new translation"
    upload_po_translation.value = ["new translation"]
    upload_po_translation.save()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["unchanged"] == 1
    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_flags_matching_suggestion(
    pretranslator, project_locale_a, upload_po_translation
):
    """A suggestion matching the upload becomes a pretranslation, keeping its author."""
    author = upload_po_translation.user
    upload_po_translation.string = "new translation"
    upload_po_translation.value = ["new translation"]
    upload_po_translation.save()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["converted"] == 1
    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1

    upload_po_translation.refresh_from_db()

    assert upload_po_translation.pretranslated
    assert upload_po_translation.active
    assert not upload_po_translation.approved
    assert upload_po_translation.user == author


@pytest.mark.django_db
def test_upload_pretranslations_keeps_other_suggestions(
    pretranslator, project_locale_a, upload_po_translation
):
    """Suggestions that do not match the upload are kept as unreviewed suggestions."""
    upload_po_translation.active = True
    upload_po_translation.save()

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 200
    assert response.json()["created"] == 1

    upload_po_translation.refresh_from_db()

    assert not upload_po_translation.rejected
    assert not upload_po_translation.pretranslated
    assert not upload_po_translation.active

    new_translation = Translation.objects.get(string="new translation")

    assert new_translation.pretranslated
    assert new_translation.active


@pytest.mark.django_db
def test_upload_pretranslations_unknown_keys_ignored(
    pretranslator, project_locale_a, upload_po_translation
):
    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
        contents='msgid "test_key"\nmsgstr "new translation"\n\n'
        'msgid "no_such_key"\nmsgstr "x"\n',
    )

    assert response.status_code == 200
    assert response.json() == {
        "created": 1,
        "replaced": 0,
        "converted": 0,
        "unchanged": 0,
        "skipped": 0,
        "failed_checks": [],
        "failed_checks_count": 0,
        "undefined_keys": [["no_such_key"]],
        "undefined_keys_count": 1,
    }


def _review_during_import(monkeypatch, review):
    """Call `review` from inside a running pretranslation import.

    `import_uploaded_pretranslations()` calls `timezone.now()` after reading the
    current translations and before writing anything, so this reproduces a review
    landing in the window the conflict check guards.
    """
    from pontoon.sync import upload as sync_upload

    real_now = sync_upload.timezone.now
    reviewed = False

    def now_and_review():
        nonlocal reviewed
        if not reviewed:
            reviewed = True
            review()
        return real_now()

    monkeypatch.setattr(
        sync_upload, "timezone", SimpleNamespace(now=now_and_review), raising=False
    )


def _approve_during_import(monkeypatch, translation, user):
    _review_during_import(monkeypatch, lambda: translation.approve(user))


@pytest.mark.django_db
def test_upload_pretranslations_conflicts_with_concurrent_approval_of_pretranslation(
    monkeypatch, pretranslator, project_locale_a, upload_po_translation, admin
):
    """A pretranslation approved mid-import is not rejected and replaced."""
    upload_po_translation.pretranslated = True
    upload_po_translation.active = True
    upload_po_translation.save()

    _approve_during_import(monkeypatch, upload_po_translation, admin)

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 409

    # The import is rolled back, which also undoes the approval made inside it.
    upload_po_translation.refresh_from_db()

    assert not upload_po_translation.rejected
    assert upload_po_translation.pretranslated
    assert upload_po_translation.active
    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_conflicts_with_concurrent_approval_of_suggestion(
    monkeypatch, pretranslator, project_locale_a, upload_po_translation, admin
):
    """A matching suggestion approved mid-import is not converted to a pretranslation."""
    upload_po_translation.active = True
    upload_po_translation.string = "new translation"
    upload_po_translation.value = ["new translation"]
    upload_po_translation.save()

    _approve_during_import(monkeypatch, upload_po_translation, admin)

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 409

    upload_po_translation.refresh_from_db()

    assert not upload_po_translation.pretranslated
    assert not upload_po_translation.approved
    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_conflicts_with_concurrent_rejection_of_suggestion(
    monkeypatch, pretranslator, project_locale_a, upload_po_translation, admin
):
    """A matching suggestion rejected mid-import is not converted to a pretranslation."""
    upload_po_translation.active = True
    upload_po_translation.string = "new translation"
    upload_po_translation.value = ["new translation"]
    upload_po_translation.save()

    _review_during_import(monkeypatch, lambda: upload_po_translation.reject(admin))

    response = _upload_pretranslation(
        _pat_client(pretranslator.user),
        project_locale_a,
        upload_po_translation.entity.resource.path,
    )

    assert response.status_code == 409

    upload_po_translation.refresh_from_db()

    assert not upload_po_translation.rejected
    assert not upload_po_translation.pretranslated
    assert Translation.objects.filter(entity=upload_po_translation.entity).count() == 1
