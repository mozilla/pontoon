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

    assert isinstance(response.data, dict)
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
    assert isinstance(response.data, dict)
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
def test_projects(
    django_assert_num_queries,
):
    with django_assert_num_queries(4):
        response = APIClient().get("/api/v2/projects/")

    assert response.status_code == 200
    assert isinstance(response.data, dict)

    project_terminology = {
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
        ],
    }
    assert project_terminology in response.data["results"]


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

    project_terminology = {
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
        ],
    }
    assert project_terminology in response.data["results"]


@pytest.mark.django_db
def test_project_locale():
    response = APIClient().get(
        "/api/v2/af/terminology/", HTTP_ACCEPT="application/json"
    )
    assert response.status_code == 200
    assert isinstance(response.data, dict)

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
    assert isinstance(response.data, dict)

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
    assert isinstance(response.data, dict)

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
