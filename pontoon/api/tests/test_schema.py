import sys

from itertools import product

import pytest

from pontoon.base.models import Project, ProjectLocale, TranslationMemoryEntry
from pontoon.terminology.models import Term, TermTranslation
from pontoon.test.factories import ProjectFactory


@pytest.fixture
def setup_excepthook():
    # graphql-core's ExecutionContext.report_error uses sys.excepthook to
    # print error stack traces. According to Python docs this hooks can be
    # safely customized:
    #
    #     The handling of such top-level exceptions can be customized by
    #     assigning another three-argument function to sys.excepthook.
    #
    # Cf. https://docs.python.org/2/library/sys.html#sys.excepthook
    excepthook_orig = sys.excepthook
    sys.excepthook = lambda *x: None
    yield
    sys.excepthook = excepthook_orig


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


@pytest.mark.django_db
def test_projects(client):
    body = {
        "query": """{
            projects(includeSystem: true) {
                name
            }
        }"""
    }

    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")

    ProjectFactory.create(visibility=Project.Visibility.PRIVATE)
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "projects": [
                {"name": "Pontoon Intro"},
                {"name": "Terminology"},
                {"name": "Tutorial"},
            ]
        }
    }


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
        Project.objects.filter(slug__in=["pontoon-intro", "tutorial"])
    )


@pytest.fixture()
def private_projects():
    return ProjectFactory.create_batch(3, visibility=Project.Visibility.PRIVATE)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "include_disabled,include_system,is_admin",
    # Produces a product with all possible project filters combinations
    product(*([[True, False]] * 3)),
)
def test_project_filters(
    include_disabled,
    include_system,
    is_admin,
    regular_projects,
    disabled_projects,
    system_projects,
    private_projects,
    client,
    admin,
):
    expected_projects = set(
        regular_projects
        + (disabled_projects if include_disabled else [])
        + (system_projects if include_system else [])
        + (private_projects if is_admin else [])
    )
    body = {
        "query": """{{
            projects(includeDisabled: {include_disabled}, includeSystem: {include_system}) {{
                slug,
                disabled,
                systemProject,
                visibility
            }}
        }}""".format(
            include_disabled=str(include_disabled).lower(),
            include_system=str(include_system).lower(),
        )
    }
    if is_admin:
        client.force_login(admin)
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "projects": [
                {
                    "slug": p.slug,
                    "visibility": p.visibility,
                    "systemProject": p.system_project,
                    "disabled": p.disabled,
                }
                for p in sorted(expected_projects, key=lambda p: p.pk)
            ]
        }
    }


@pytest.mark.django_db
def test_project_localizations(client):
    body = {
        "query": """{
            project(slug: "pontoon-intro") {
                localizations {
                    locale {
                        name,
                        stringsWithErrors
                    }
                }
            }
        }"""
    }

    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "project": {
                "localizations": [
                    {"locale": {"name": "English", "stringsWithErrors": 0}}
                ]
            }
        }
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "include_disabled,include_system,is_admin",
    # Produces a product with all possible filters combinations
    product(*([[True, False]] * 3)),
)
def test_localization_filters(
    include_disabled,
    include_system,
    is_admin,
    locale_a,
    regular_projects,
    disabled_projects,
    system_projects,
    private_projects,
    client,
    admin,
):
    expected_projects = set(
        regular_projects
        + (disabled_projects if include_disabled else [])
        + (system_projects if include_system else [])
        + (private_projects if is_admin else [])
    )
    ProjectLocale.objects.bulk_create(
        [
            ProjectLocale(project=p, locale=locale_a)
            for p in expected_projects
            if p.slug not in ("pontoon-intro", "tutorial", "terminology")
        ]
    )

    body = {
        "query": """{{
            locale (code: \"{locale_code}\") {{
                localizations(includeDisabled: {include_disabled}, includeSystem: {include_system}) {{
                    project {{
                        slug,
                        disabled,
                        systemProject,
                        visibility
                    }}
                }}
            }}
        }}""".format(
            locale_code=locale_a.code,
            include_disabled=str(include_disabled).lower(),
            include_system=str(include_system).lower(),
        )
    }

    if is_admin:
        client.force_login(admin)

    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "locale": {
                "localizations": [
                    {
                        "project": {
                            "slug": p.slug,
                            "visibility": p.visibility,
                            "systemProject": p.system_project,
                            "disabled": p.disabled,
                        }
                    }
                    for p in sorted(
                        expected_projects,
                        key=lambda p: p.project_locale.filter(locale=locale_a)[0].pk,
                    )
                ]
            }
        }
    }


@pytest.mark.django_db
def test_projects_localizations_cyclic(client):
    body = {
        "query": """{
            projects {
                localizations {
                    locale {
                        localizations {
                            totalStrings
                        }
                    }
                }
            }
        }"""
    }

    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert b"Cyclic queries are forbidden" in response.content


@pytest.mark.django_db
def test_project_localizations_cyclic(client):
    body = {
        "query": """{
            project(slug: "pontoon-intro") {
                localizations {
                    locale {
                        localizations {
                            totalStrings
                        }
                    }
                }
            }
        }"""
    }

    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert b"Cyclic queries are forbidden" in response.content


@pytest.mark.django_db
def test_locales_localizations_cyclic(client):
    body = {
        "query": """{
            locales {
                localizations {
                    project {
                        localizations {
                            totalStrings
                        }
                    }
                }
            }
        }"""
    }

    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert b"Cyclic queries are forbidden" in response.content


@pytest.mark.django_db
def test_locale_localizations_cyclic(client):
    body = {
        "query": """{
            locale(code: "en-US") {
                localizations {
                    project {
                        localizations {
                            totalStrings
                        }
                    }
                }
            }
        }"""
    }

    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert b"Cyclic queries are forbidden" in response.content


@pytest.mark.django_db
def test_term_search_by_text(client, terms):
    """Test searching terms by their text field."""
    body = {
        "query": """{
            termSearch(search: "open", locale: "kg") {
                text
                translationText
            }
        }"""
    }
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "termSearch": [
                {
                    "text": "open",
                    "translationText": "odpreti",
                }
            ]
        }
    }


@pytest.mark.django_db
def test_term_search_by_translation(client, terms):
    """Test searching terms by their translations."""
    body = {
        "query": """{
            termSearch(search: "odpreti", locale: "kg") {
                text
                translationText
            }
        }"""
    }
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "termSearch": [
                {
                    "text": "open",
                    "translationText": "odpreti",
                }
            ]
        }
    }


@pytest.mark.django_db
def test_term_search_no_match(client, terms):
    """Test searching with a term that doesn't match any text or translations."""
    body = {
        "query": """{
            termSearch(search: "nonexistent", locale: "kg") {
                text
                translationText
            }
        }"""
    }
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    assert response.json() == {"data": {"termSearch": []}}


@pytest.mark.django_db
def test_term_search_multiple_matches(client, terms):
    """Test searching with a term that matches multiple results."""
    body = {
        "query": """{
            termSearch(search: "o", locale: "kg") {
                text
                translationText
            }
        }"""
    }
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")
    assert response.status_code == 200

    # Sort the response data to ensure order doesn't affect test results
    actual_data = response.json()["data"]["termSearch"]
    expected_data = [
        {"text": "close", "translationText": "zapreti"},
        {"text": "open", "translationText": "odpreti"},
    ]
    assert sorted(actual_data, key=lambda x: x["text"]) == sorted(
        expected_data, key=lambda x: x["text"]
    )


@pytest.mark.django_db
def test_term_search_no_translations(client, terms):
    """Test searching terms for a locale with no translations."""
    body = {
        "query": """{
            termSearch(search: "open", locale: "en") {
                text
                translationText
            }
        }"""
    }
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "termSearch": [
                {
                    "text": "open",
                    "translationText": None,
                }
            ]
        }
    }


@pytest.mark.django_db
def test_tm_search_by_source(client, tm_entries):
    """Test searching TM entries by source text."""
    body = {
        "query": """{
            tmSearch(search: "Hello", locale: "kg") {
                source
                target
            }
        }"""
    }
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "tmSearch": [
                {
                    "source": "Hello",
                    "target": "Hola",
                }
            ]
        }
    }


@pytest.mark.django_db
def test_tm_search_by_target(client, tm_entries):
    """Test searching TM entries by target text."""
    body = {
        "query": """{
            tmSearch(search: "Hola", locale: "kg") {
                source
                target
            }
        }"""
    }
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "tmSearch": [
                {
                    "source": "Hello",
                    "target": "Hola",
                }
            ]
        }
    }


@pytest.mark.django_db
def test_tm_search_no_match(client, tm_entries):
    """Test TM search with a query that doesn't match any entry."""
    body = {
        "query": """{
            tmSearch(search: "Nonexistent", locale: "kg") {
                source
                target
            }
        }"""
    }
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    assert response.json() == {"data": {"tmSearch": []}}


@pytest.mark.django_db
def test_tm_search_multiple_matches(client, tm_entries):
    """Test TM search with a query that matches multiple entries."""
    body = {
        "query": """{
            tmSearch(search: "o", locale: "kg") {
                source
                target
                project {
                    slug
                }
            }
        }"""
    }
    response = client.get("/graphql/", body, HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "tmSearch": [
                {
                    "source": "Hello",
                    "target": "Hola",
                    "project": {
                        "slug": "project_a",
                    },
                },
                {
                    "source": "Goodbye",
                    "target": "Adiós",
                    "project": {
                        "slug": "project_b",
                    },
                },
            ]
        }
    }
