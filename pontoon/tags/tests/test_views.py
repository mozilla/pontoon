import pytest

from django.urls import reverse

from pontoon.base.models import Priority


@pytest.mark.django_db
def test_view_project_tag_locales(client, project_a, tag_a):
    url = reverse(
        "pontoon.tags.project.tag",
        kwargs=dict(project=project_a.slug, tag=tag_a.slug),
    )

    # tag is not associated with project
    project_a.tag_set.remove(tag_a)
    response = client.get(url)
    assert response.status_code == 404

    project_a.tag_set.add(tag_a)
    tag_a.priority = Priority.NORMAL
    tag_a.save()
    response = client.get(url)
    assert response.status_code == 200

    # the response is not json
    with pytest.raises(ValueError):
        response.json()

    assert response.template_name == ["tags/tag.html"]
    assert response.context_data["project"] == project_a

    res_tag = response.context_data["tag"]
    assert res_tag == tag_a


@pytest.mark.django_db
def test_view_project_tag_locales_ajax(client, project_a, tag_a):
    url = reverse(
        "pontoon.tags.ajax.teams",
        kwargs=dict(project=project_a.slug, tag=tag_a.slug),
    )
    project_a.tag_set.add(tag_a)
    tag_a.priority = Priority.NORMAL
    tag_a.save()
    response = client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    # the response is not json even with xhr headers
    with pytest.raises(ValueError):
        response.json()

    assert response.template_name == ["projects/includes/teams.html"]
    assert response.context_data["project"] == project_a

    locales = project_a.project_locale.all()
    assert len(response.context_data["locales"]) == locales.count()

    for i, locale in enumerate(locales):
        locale = response.context_data["locales"][i]
        assert locale.code == locales[i].locale.code
        assert locale.name == locales[i].locale.name


@pytest.mark.django_db
def test_view_project_tag_ajax(client, project_a, tag_a):
    url = reverse(
        "pontoon.projects.ajax.tags",
        kwargs=dict(slug=project_a.slug),
    )
    project_a.tag_set.add(tag_a)
    tag_a.priority = Priority.NORMAL
    tag_a.save()

    response = client.get(url)
    assert response.status_code == 400

    response = client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    # response returns html
    with pytest.raises(ValueError):
        response.json()
    assert tag_a.name.encode("utf-8") in response.content
    assert tag_a.slug.encode("utf-8") in response.content
