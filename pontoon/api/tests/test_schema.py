import sys
from itertools import product

import pytest
from pontoon.base.models import Project, ProjectLocale

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


@pytest.mark.django_db
def test_projects(client):
    body = {
        "query": """{
            projects(includeSystem: true) {
                name
            }
        }"""
    }

    response = client.get("/graphql", body, HTTP_ACCEPT="application/json")

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
    response = client.get("/graphql", body, HTTP_ACCEPT="application/json")

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
                        name
                    }
                }
            }
        }"""
    }

    response = client.get("/graphql", body, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert response.json() == {
        "data": {"project": {"localizations": [{"locale": {"name": "English"}}]}}
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

    response = client.get("/graphql", body, HTTP_ACCEPT="application/json")

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

    response = client.get("/graphql", body, HTTP_ACCEPT="application/json")

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

    response = client.get("/graphql", body, HTTP_ACCEPT="application/json")

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

    response = client.get("/graphql", body, HTTP_ACCEPT="application/json")

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

    response = client.get("/graphql", body, HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert b"Cyclic queries are forbidden" in response.content
