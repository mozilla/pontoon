import json

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from django.http import Http404

from pontoon.base.models import Resource
from pontoon.base.views import (
    AjaxFormPostView,
    AjaxFormView,
    get_fluent_terms,
    get_sibling_entities,
    get_team_comments,
    get_translation_history,
    get_translations_from_other_locales,
    locale_project_parts,
)
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
    UserFactory,
)
from pontoon.translations.utils import parse_source_string_to_json


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
    assert {data["title"] for data in json.loads(response.content)} == {
        "/other/path.po",
        "all-resources",
    }

    request_c = rf.get(
        f"/{locale_c.code}/{project.slug}/parts", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    request_c.user = UserFactory()
    response = locale_project_parts(request_c, locale_c.code, project.slug)
    assert response.status_code == 200
    assert {data["title"] for data in json.loads(response.content)} == {
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
@pytest.mark.parametrize(
    "query",
    [
        # Missing project parameter
        "locale=ab",
        # Missing locale parameter
        "project=project_a",
    ],
)
def test_get_fluent_terms_bad_request(rf, user_a, query):
    """Test a 400 response for missing parameters."""
    request = rf.get(
        f"/get-fluent-terms/?{query}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_terms(request)

    assert response.status_code == 400


@pytest.mark.django_db
def test_get_fluent_terms_invalid_locale(rf, user_a, project_a):
    """Test a 404 response for a non-existent locale."""
    request = rf.get(
        f"/get-fluent-terms/?project={project_a.slug}&locale=invalid-locale",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    with pytest.raises(Http404):
        get_fluent_terms(request)


@pytest.mark.django_db
def test_get_fluent_terms_private_project_access(rf, user_a, admin, locale_a):
    """Test a 404 response for a private project for a non-admin user."""
    project_a = ProjectFactory(name="Project A", visibility="private")
    ResourceFactory(project=project_a)

    request = rf.get(
        f"/get-fluent-terms/?project={project_a.slug}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    with pytest.raises(Http404):
        get_fluent_terms(request)

    request.user = admin
    response = get_fluent_terms(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_terms_no_terms(rf, user_a, locale_a, project_a):
    """Test an empty payload for a project without Fluent terms."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    EntityFactory(
        resource=resource_a,
        string="message = Hello",
    )

    request = rf.get(
        f"/get-fluent-terms/?project={project_a.slug}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_terms(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_terms_non_fluent_resource(rf, user_a, locale_a, project_a):
    """Test an empty payload for a project with only non-Fluent resources."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.dtd",
        format=Resource.Format.DTD,
    )
    entity_a = EntityFactory(
        resource=resource_a,
        string="-brand-term = about Brand",
    )
    TranslationFactory(
        entity=entity_a,
        locale=locale_a,
        active=True,
        approved=True,
        string="-brand-term = about Brand-localized",
    )

    request = rf.get(
        f"/get-fluent-terms/?project={project_a.slug}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_terms(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_terms_happy_path(rf, user_a, locale_a, project_a):
    """Test fetching all terms in a project with their translations."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    # Term with translation.
    entity_term = EntityFactory(
        resource=resource_a,
        string="-brand-term = about Brand",
    )
    translation = TranslationFactory(
        entity=entity_term,
        locale=locale_a,
        active=True,
        approved=True,
        string=(
            "-brand-term = { $case ->\n"
            "   *[nominative] Brand-nom\n"
            "    [accusative] Brand-acc\n"
            "}"
        ),
    )
    # Term without translation.
    entity_term_no_translation = EntityFactory(
        resource=resource_a,
        string="-other-term = Other",
    )
    # Regular message.
    EntityFactory(
        resource=resource_a,
        string="message = This uses { -brand-term }",
    )

    request = rf.get(
        f"/get-fluent-terms/?project={project_a.slug}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_terms(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "-brand-term": {
            "value": entity_term.value,
            "properties": entity_term.properties,
            "translation_value": translation.value,
            "translation_properties": translation.properties,
        },
        "-other-term": {
            "value": entity_term_no_translation.value,
            "properties": entity_term_no_translation.properties,
            "translation_value": None,
            "translation_properties": None,
        },
    }


@pytest.mark.django_db
def test_get_fluent_terms_term_with_attributes(rf, user_a, locale_a, project_a):
    """Test term attributes are included in value and translation payloads."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_term = EntityFactory(
        resource=resource_a,
        string=(
            "-brand-term = Brand\n"
            "    .case = { $case ->\n"
            "       *[nom] Brand\n"
            "        [gen] Brand's\n"
            "    }"
        ),
    )
    translation_string = (
        "-brand-term = Brand\n"
        "    .case = { $case ->\n"
        "       *[nom] Brand-nom\n"
        "        [gen] Brand-gen\n"
        "    }"
    )
    _, translation_value, translation_properties = parse_source_string_to_json(
        Resource.Format.FLUENT, translation_string
    )
    translation = TranslationFactory(
        entity=entity_term,
        locale=locale_a,
        active=True,
        approved=True,
        string=translation_string,
        value=translation_value,
        properties=translation_properties,
    )

    request = rf.get(
        f"/get-fluent-terms/?project={project_a.slug}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_terms(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "-brand-term": {
            "value": entity_term.value,
            "properties": entity_term.properties,
            "translation_value": translation.value,
            "translation_properties": translation.properties,
        },
    }


@pytest.mark.django_db
def test_get_fluent_terms_obsolete_term(rf, user_a, locale_a, project_a):
    """Test obsolete terms are not returned."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    EntityFactory(
        resource=resource_a,
        string="-brand-term = about Brand",
        obsolete=True,
    )

    request = rf.get(
        f"/get-fluent-terms/?project={project_a.slug}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_terms(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_terms_inactive_translation(rf, user_a, locale_a, project_a):
    """Test inactive translations are not used."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_term = EntityFactory(
        resource=resource_a,
        string="-brand-term = about Brand",
    )
    TranslationFactory(
        entity=entity_term,
        locale=locale_a,
        active=False,
        approved=False,
        string="-brand-term = Brand",
    )

    request = rf.get(
        f"/get-fluent-terms/?project={project_a.slug}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_terms(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "-brand-term": {
            "value": entity_term.value,
            "properties": entity_term.properties,
            "translation_value": None,
            "translation_properties": None,
        },
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("factory_kwargs", "expected"),
    [
        ({"active": True, "approved": True}, True),
        ({"active": True, "approved": False, "fuzzy": True}, True),
        ({"active": False, "approved": True}, False),
    ],
)
def test_get_fluent_terms_translation_selection(
    rf, user_a, locale_a, project_a, factory_kwargs, expected
):
    """Test only the active translation is used."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_term = EntityFactory(
        resource=resource_a,
        string="-brand-term = about Brand",
    )
    TranslationFactory(
        entity=entity_term,
        locale=locale_a,
        string="-brand-term = translated",
        **factory_kwargs,
    )

    request = rf.get(
        f"/get-fluent-terms/?project={project_a.slug}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_terms(request)

    assert response.status_code == 200
    payload = json.loads(response.content)
    has_translation_value = payload["-brand-term"]["translation_value"] is not None
    assert has_translation_value is expected


@pytest.mark.django_db
def test_get_translation_history(rf, user_a, admin):
    project_a = ProjectFactory(name="Project A", visibility="private")
    resource_a = ResourceFactory(project=project_a)
    entity_a = EntityFactory(string="Entity A", resource=resource_a)
    locale_a = LocaleFactory(code="gs", name="Geonosian")

    request_a = rf.get(
        f"/get-history/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_a.user = user_a

    with pytest.raises(Http404):
        get_translation_history(request_a)

    request_b = rf.get(
        f"/get-history/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_b.user = admin

    response = get_translation_history(request_b)

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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "view",
    [
        get_translations_from_other_locales,
        get_sibling_entities,
        get_translation_history,
        get_team_comments,
    ],
)
def test_translate_view_endpoints_reach_system_projects(rf, user_a, view):
    """The tutorial is a system project: kept off the dashboards, but translated
    in the same UI as any other project, so these endpoints have to serve it."""
    project = ProjectFactory(
        name="System Project", slug="system-project", system_project=True
    )
    resource = ResourceFactory(project=project)
    entity = EntityFactory(string="Entity", resource=resource)
    locale = LocaleFactory(code="gs", name="Geonosian")

    request = rf.get(
        f"/?entity={entity.id}&locale={locale.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    assert view(request).status_code == 200
