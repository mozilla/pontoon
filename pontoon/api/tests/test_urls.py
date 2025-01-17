import pytest


@pytest.fixture
@pytest.mark.django_db
def projects_query():
    return {"query": "{projects{name}}"}


@pytest.mark.django_db
def test_graphql_json_get(settings, projects_query, client):
    response = client.get("/graphql/", projects_query, HTTP_ACCEPT="application/json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_graphql_json_post(settings, projects_query, client):
    response = client.post("/graphql/", projects_query, HTTP_ACCEPT="application/json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_graphiql_html_get(settings, projects_query, client):
    response = client.get("/graphql/", projects_query, HTTP_ACCEPT="text/html")
    assert response.status_code == 200


@pytest.mark.django_db
def test_graphiql_html_post(settings, projects_query, client):
    response = client.post("/graphql/", projects_query, HTTP_ACCEPT="text/html")
    assert response.status_code == 200
