import sys

import pytest


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
