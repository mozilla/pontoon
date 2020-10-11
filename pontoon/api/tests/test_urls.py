from __future__ import absolute_import

import sys
import pytest
from django.urls import clear_url_caches

from six.moves import reload_module


def reload_urls(settings):
    clear_url_caches()
    reload_module(sys.modules[settings.ROOT_URLCONF])


@pytest.fixture
@pytest.mark.django_db
def projects_query():
    return {"query": "{projects{name}}"}


@pytest.mark.django_db
def test_graphql_dev_get(settings, projects_query, client):
    settings.DEV = True

    response = client.get("/graphql", projects_query, HTTP_ACCEPT="application/json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_graphql_dev_post(settings, projects_query, client):
    settings.DEV = True

    response = client.post("/graphql", projects_query, HTTP_ACCEPT="application/json")
    assert response.status_code == 200


@pytest.mark.skipif(reason="Overriding DEV does not work.")
@pytest.mark.django_db
def test_graphql_prod_get(settings, projects_query, client):
    settings.DEV = True

    response = client.get("/graphql", projects_query, HTTP_ACCEPT="application/json")
    assert response.status_code == 200


@pytest.mark.skipif(reason="Overriding DEV does not work.")
@pytest.mark.django_db
def test_graphql_prod_post(settings, projects_query, client):
    settings.DEV = False

    response = client.post("/graphql", projects_query, HTTP_ACCEPT="appication/json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_graphiql_dev_get(settings, projects_query, client):
    settings.DEV = True

    response = client.get("/graphql", projects_query, HTTP_ACCEPT="text/html")
    assert response.status_code == 200


@pytest.mark.django_db
def test_graphiql_dev_post(settings, projects_query, client):
    settings.DEV = True
    response = client.post("/graphql", projects_query, HTTP_ACCEPT="text/html")
    assert response.status_code == 200


@pytest.mark.skipif(reason="Overriding DEV does not work.")
@pytest.mark.django_db
def test_graphiql_prod_get(settings, projects_query, client):
    settings.DEV = False
    reload_urls(settings)
    response = client.get("/graphql", projects_query, HTTP_ACCEPT="text/html")
    assert response.status_code == 400


@pytest.mark.skipif(reason="Overriding DEV does not work.")
@pytest.mark.django_db
def test_graphiql_prod_post(projects_query, client, settings):
    settings.DEV = False
    reload_urls(settings)
    response = client.post("/graphql", projects_query, HTTP_ACCEPT="text/html")
    assert response.status_code == 400
