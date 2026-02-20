import json

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from django.http import Http404

from pontoon.base.views import (
    AjaxFormPostView,
    AjaxFormView,
    get_sibling_entities,
    get_team_comments,
    get_translations_from_other_locales,
    locale_project_parts,
)
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    UserFactory,
)


@pytest.fixture
def locale_c():
    return LocaleFactory(
        code="nv",
        name="Na'vi",
    )


def test_view_ajax_form(rf):
    with (
        patch("pontoon.base.views.AjaxFormView.get_form") as form_m,
        patch("pontoon.base.views.AjaxFormView.render_to_response") as response_m,
    ):
        form_m.return_value = 7
        response_m.return_value = 23

        # needs xhr headers...
        response = AjaxFormView.as_view()(rf.get("/foo/bar"))
        assert response.status_code == 400
        assert not form_m.called

        view = AjaxFormView.as_view()
        response = view(rf.get("/foo/bar", HTTP_X_REQUESTED_WITH="XMLHttpRequest"))
        assert list(response_m.call_args)[0][0]["form"] == 7
        assert list(form_m.call_args) == [(), {}]
        assert response == 23


def test_view_ajax_form_post(rf):
    with (
        patch("pontoon.base.views.AjaxFormPostView.get_form") as form_m,
        patch("pontoon.base.views.AjaxFormPostView.render_to_response"),
    ):
        with pytest.raises(Http404):
            AjaxFormPostView.as_view()(rf.get("/foo/bar"))
        with pytest.raises(Http404):
            AjaxFormPostView.as_view()(
                rf.get("/foo/bar", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            )
        assert not form_m.called


def test_view_ajax_form_submit_bad(rf):
    with (
        patch("pontoon.base.views.AjaxFormView.get_form") as form_m,
        patch("pontoon.base.views.AjaxFormView.render_to_response") as response_m,
    ):
        _form = MagicMock()
        _form.is_valid.return_value = False
        type(_form).errors = PropertyMock(return_value=["BAD", "STUFF"])
        form_m.return_value = _form
        response_m.return_value = 23

        # needs xhr headers...
        response = AjaxFormView.as_view()(rf.post("/foo/bar", data=dict(foo=1, bar=2)))
        assert response.status_code == 400
        assert not form_m.called

        view = AjaxFormView.as_view()
        response = view(
            rf.post(
                "/foo/bar",
                data=dict(foo=1, bar=2),
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
        )
        assert response.status_code == 400
        assert json.loads(response.content) == {"errors": ["BAD", "STUFF"]}


def test_view_ajax_form_submit_success(rf):
    with (
        patch("pontoon.base.views.AjaxFormView.get_form") as form_m,
        patch("pontoon.base.views.AjaxFormView.render_to_response"),
    ):
        _form = MagicMock()
        _form.is_valid.return_value = True
        _form.save.return_value = 23
        type(_form).errors = PropertyMock(return_value=["BAD", "STUFF"])
        form_m.return_value = _form

        # needs xhr headers...
        response = AjaxFormView.as_view()(rf.post("/foo/bar", data=dict(foo=1, bar=2)))
        assert response.status_code == 400
        assert not form_m.called

        view = AjaxFormView.as_view()
        response = view(
            rf.post(
                "/foo/bar",
                data=dict(foo=1, bar=2),
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
        )
        assert response.status_code == 200
        assert json.loads(response.content) == {"data": 23}


@pytest.mark.django_db
def test_locale_parts_stats_no_page_one_resource(rf, locale_parts):
    """
    Return resource paths and stats if one resource defined.
    """
    locale_c, _, entityX = locale_parts
    project = entityX.resource.project
    request = rf.get(
        f"/{locale_c.code}/{project.slug}/parts", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    request.user = UserFactory()
    response = locale_project_parts(request, locale_c.code, project.slug)
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {
            "title": "resourceX.po",
            "approved": 0,
            "pretranslated": 0,
            "errors": 0,
            "warnings": 0,
            "total": 0,
            "unreviewed": 0,
        },
        {
            "title": "all-resources",
            "approved": 0,
            "pretranslated": 0,
            "errors": 0,
            "warnings": 0,
            "total": 0,
            "unreviewed": 0,
        },
    ]


@pytest.mark.django_db
def test_locale_parts_stats_no_page_multiple_resources(rf, locale_parts):
    """
    Return resource paths and stats for locales resources are available for.
    """
    locale_c, locale_b, entityX = locale_parts
    project = entityX.resource.project
    resourceY = ResourceFactory.create(
        total_strings=1, project=project, path="/other/path.po"
    )
    EntityFactory.create(resource=resourceY, string="Entity Y")
    TranslatedResourceFactory.create(resource=resourceY, locale=locale_b)
    TranslatedResourceFactory.create(resource=resourceY, locale=locale_c)

    request_b = rf.get(
        f"/{locale_b.code}/{project.slug}/parts", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    request_b.user = UserFactory()
    response = locale_project_parts(request_b, locale_b.code, project.slug)
    assert response.status_code == 200
    assert set(data["title"] for data in json.loads(response.content)) == {
        "/other/path.po",
        "all-resources",
    }

    request_c = rf.get(
        f"/{locale_c.code}/{project.slug}/parts", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    request_c.user = UserFactory()
    response = locale_project_parts(request_c, locale_c.code, project.slug)
    assert response.status_code == 200
    assert set(data["title"] for data in json.loads(response.content)) == {
        entityX.resource.path,
        "/other/path.po",
        "all-resources",
    }


@pytest.mark.django_db
def test_get_translations_from_other_locales_authentication(rf, user_a, admin):
    project_a = ProjectFactory(name="Project A", visibility="private")
    resource_a = ResourceFactory(project=project_a)
    entity_a = EntityFactory(string="Entity A", resource=resource_a)
    locale_a = LocaleFactory(code="gs", name="Geonosian")

    request_a = rf.get(
        f"/other-locales/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_a.user = user_a

    with pytest.raises(Http404):
        get_translations_from_other_locales(request_a)

    request_b = rf.get(
        f"/other-locales/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_b.user = admin

    response = get_translations_from_other_locales(request_b)

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_sibling_entities_authentication(rf, user_a, admin):
    project_a = ProjectFactory(name="Project A", visibility="private")
    resource_a = ResourceFactory(project=project_a)
    entity_a = EntityFactory(string="Entity A", resource=resource_a)
    locale_a = LocaleFactory(code="gs", name="Geonosian")

    request_a = rf.get(
        f"/other-locales/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_a.user = user_a

    with pytest.raises(Http404):
        get_sibling_entities(request_a)

    request_b = rf.get(
        f"/other-locales/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_b.user = admin

    response = get_sibling_entities(request_b)

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_team_comments_authentication(rf, user_a, admin):
    project_a = ProjectFactory(name="Project A", visibility="private")
    resource_a = ResourceFactory(project=project_a)
    entity_a = EntityFactory(string="Entity A", resource=resource_a)
    locale_a = LocaleFactory(code="gs", name="Geonosian")

    request_a = rf.get(
        f"/other-locales/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_a.user = user_a

    with pytest.raises(Http404):
        get_team_comments(request_a)

    request_b = rf.get(
        f"/other-locales/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_b.user = admin

    response = get_team_comments(request_b)

    assert response.status_code == 200
