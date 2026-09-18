import json

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from django.http import Http404

from pontoon.base.models import Resource
from pontoon.base.views import (
    AjaxFormPostView,
    AjaxFormView,
    get_fluent_reference_variants,
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
def test_get_fluent_reference_variants_private_project_access(
    rf, locale_a, user_a, admin
):
    """Test retrieval of entities from private projects."""
    project_a = ProjectFactory(name="Project A", visibility="private")
    resource_a = ResourceFactory(project=project_a)
    entity_a = EntityFactory(string="Entity A", resource=resource_a)

    request_a = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_a.user = user_a

    with pytest.raises(Http404):
        get_fluent_reference_variants(request_a)

    request_b = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_a.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request_b.user = admin

    response = get_fluent_reference_variants(request_b)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_reference_variants_invalid_locale(rf, user_a, project_a):
    """Test a 404 response for a non-existent locale."""
    resource_a = ResourceFactory(project=project_a)
    entity_a = EntityFactory(string="Entity A", resource=resource_a)

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_a.id}&locale=invalid-locale",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    with pytest.raises(Http404):
        get_fluent_reference_variants(request)


@pytest.mark.django_db
def test_get_fluent_reference_variants_nonexistent_entity(
    rf, user_a, locale_a, project_a
):
    """Test a 404 response for a non-existent entity."""
    request = rf.get(
        "/get-fluent-reference-variants/?entity=1234&locale=ab",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    with pytest.raises(Http404):
        get_fluent_reference_variants(request)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "query",
    [
        # Missing entity parameter
        "locale=ab",
        # Missing locale parameter
        "entity=1",
        # Non-integer entity parameter
        "entity=abc&locale=ab",
    ],
)
def test_get_fluent_reference_variants_bad_request(rf, user_a, query):
    """Test a 400 response for missing or invalid parameters."""
    request = rf.get(
        f"/get-fluent-reference-variants/?{query}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 400


@pytest.mark.django_db
def test_get_fluent_reference_variants_non_fluent_resource(
    rf, user_a, locale_a, project_a
):
    """Test no variants are returned for a non-Fluent resource."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.dtd",
        format=Resource.Format.DTD,
    )
    entity_term = EntityFactory(
        resource=resource_a,
        string="-brand-term = about Brand",
    )
    TranslationFactory(
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

    entity_current = EntityFactory(
        resource=resource_a,
        string="message = { -brand-term }",
    )

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_reference_variants_happy_path(rf, user_a, locale_a, project_a):
    """Test fetching term variants for a locale."""
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
        active=True,
        approved=True,
        string=(
            "-brand-term = { $case ->\n"
            "   *[nominative] Brand-nom\n"
            "    [accusative] Brand-acc\n"
            "}"
        ),
    )

    entity_current = EntityFactory(
        resource=resource_a,
        string="message = This uses { -brand-term }",
    )

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "-brand-term": [{"name": "case", "values": ["accusative", "nominative"]}],
    }


@pytest.mark.django_db
def test_get_fluent_reference_variants_no_selector(rf, user_a, locale_a, project_a):
    """Test retrieving variants from a translation that has no selector."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_term = EntityFactory(
        resource=resource_a,
        string=(
            "-brand-term = { $case ->\n"
            "   *[nominative] Brand-nom\n"
            "    [genitive] Brand-gen\n"
            "}"
        ),
    )
    TranslationFactory(
        entity=entity_term,
        locale=locale_a,
        active=True,
        approved=True,
        string=("-brand-term = no selectors in translation"),
    )

    entity_current = EntityFactory(
        resource=resource_a,
        string="message = { -brand-term }",
    )

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_reference_variants_dangling_term_reference(
    rf, user_a, locale_a, project_a
):
    """Test no variant fields are returned for a term without a matching entity."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_current = EntityFactory(
        resource=resource_a,
        string="message = { -brand-term }",
    )

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_reference_variants_obsolete_term(rf, user_a, locale_a, project_a):
    """Test no variant fields are returned for an obsolete term entity."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_term = EntityFactory(
        resource=resource_a,
        string="-brand-term = Brand",
        obsolete=True,
    )
    TranslationFactory(
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

    entity_current = EntityFactory(
        resource=resource_a,
        string="message = { -brand-term }",
    )

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_reference_variants_no_translation(rf, user_a, locale_a, project_a):
    """Test no variant fields are returned without a translation."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    _entity_term = EntityFactory(
        resource=resource_a,
        string=(
            "-brand-term = { $case ->\n"
            "   *[nominative] Brand-nom\n"
            "    [genitive] Brand-gen\n"
            "}"
        ),
    )

    entity_current = EntityFactory(
        resource=resource_a,
        string="message = { -brand-term }",
    )

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_reference_variants_inactive_translation(
    rf, user_a, locale_a, project_a
):
    """Test variants come only from the active translation."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_term = EntityFactory(
        resource=resource_a,
        string="-brand-term = Brand",
    )
    TranslationFactory(
        entity=entity_term,
        locale=locale_a,
        active=True,
        approved=True,
        string="-brand-term = Brand",
    )
    TranslationFactory(
        entity=entity_term,
        locale=locale_a,
        active=False,
        approved=False,
        string=(
            "-brand-term = { $case ->\n"
            "   *[nominative] Brand-nom\n"
            "    [accusative] Brand-acc\n"
            "}"
        ),
    )

    entity_current = EntityFactory(
        resource=resource_a,
        string="message = { -brand-term }",
    )

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_get_fluent_reference_variants_multiple_terms(rf, user_a, locale_a, project_a):
    """Test variant retrieval for an entity referencing multiple terms."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    _entity_term_a = EntityFactory(
        resource=resource_a,
        string=("-brand-term = Brand"),
    )
    entity_term_b = EntityFactory(
        resource=resource_a,
        string=("-brand-short-term = Brand-Short"),
    )
    TranslationFactory(
        entity=entity_term_b,
        locale=locale_a,
        active=True,
        approved=True,
        string=(
            "-brand-short-term = { $case ->\n"
            "   *[nominative] Brand-Short-nom\n"
            "    [accusative] Brand-Short-acc\n"
            "}"
        ),
    )

    entity_current = EntityFactory(
        resource=resource_a,
        string="message = { -brand-term } or { -brand-short-term }",
    )

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "-brand-short-term": [{"name": "case", "values": ["accusative", "nominative"]}]
    }


@pytest.mark.django_db
def test_get_fluent_reference_variants_multiple_resources(
    rf, user_a, locale_a, project_a
):
    """Test prioritizing the current entity's resource over another resource in the project."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_term_a = EntityFactory(
        resource=resource_a,
        string="-brand-term = Brand From A",
    )
    TranslationFactory(
        entity=entity_term_a,
        locale=locale_a,
        active=True,
        approved=True,
        string=(
            "-brand-term = { $case-a ->\n"
            "   *[nominative-a] Brand-A-nom\n"
            "    [accusative-a] Brand-A-acc\n"
            "}"
        ),
    )

    resource_b = ResourceFactory(
        project=project_a,
        path="b.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_term_b = EntityFactory(
        resource=resource_b,
        string="-brand-term = Brand From B",
    )
    TranslationFactory(
        entity=entity_term_b,
        locale=locale_a,
        active=True,
        approved=True,
        string=(
            "-brand-term = { $case-b ->\n"
            "   *[nominative-b] Brand-B-nom\n"
            "    [accusative-b] Brand-B-acc\n"
            "}"
        ),
    )

    entity_current = EntityFactory(
        resource=resource_a,
        string="message= { -brand-term }",
    )

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "-brand-term": [{"name": "case-a", "values": ["accusative-a", "nominative-a"]}],
    }


@pytest.mark.django_db
def test_get_fluent_reference_variants_term_in_other_resource_fallback(
    rf, user_a, locale_a, project_a
):
    """Test falling back to the term defined in another resource of the project."""
    resource_a = ResourceFactory(
        project=project_a,
        path="a.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_current = EntityFactory(
        resource=resource_a,
        string="message = { -brand-term }",
    )

    resource_b = ResourceFactory(
        project=project_a,
        path="b.ftl",
        format=Resource.Format.FLUENT,
    )
    entity_term_b = EntityFactory(
        resource=resource_b,
        string="-brand-term = Brand",
    )
    TranslationFactory(
        entity=entity_term_b,
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

    request = rf.get(
        f"/get-fluent-reference-variants/?entity={entity_current.id}&locale={locale_a.code}",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user_a

    response = get_fluent_reference_variants(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "-brand-term": [{"name": "case", "values": ["accusative", "nominative"]}],
    }


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
