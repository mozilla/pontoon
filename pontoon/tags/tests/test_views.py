import factory
import pytest
from mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse

from pontoon.tags.models import Tag
from pontoon.tags.utils import TaggedLocale, TagTool
from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    Resource,
    TranslatedResource,
)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()


@pytest.fixture
def fake_user():
    return UserFactory(
        username="fake_user",
        email="fake_user@example.org"
    )


@pytest.fixture
def member(client, fake_user):
    client.force_login(fake_user)
    return client


@pytest.fixture
def admin():
    """Admin - a superuser"""
    return get_user_model().objects.create(
        username="admin",
        email="admin@example.org",
        is_superuser=True,
    )


@pytest.fixture
def locale():
    return Locale.objects.create(
        code="kg",
        name="Klingon",
    )


@pytest.fixture
def project():
    return Project.objects.create(
        slug="project", name="Project"
    )


@pytest.fixture
def resource(project, locale, fake_user):
    # Tags require a ProjectLocale to work.
    ProjectLocale.objects.create(project=project, locale=locale)
    resource = Resource.objects.create(
        project=project, path="resource.po", format="po"
    )
    # Tags require a TranslatedResource to work.
    TranslatedResource.objects.create(
        resource=resource, locale=locale
    )
    resource.total_strings = 1
    resource.save()
    return resource


@pytest.fixture
def tag(resource):
    tag = Tag.objects.create(slug="tag", name="Tag")
    tag.resources.add(resource)
    return tag


@pytest.mark.django_db
@patch('pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form_class')
def test_view_project_tag_admin_ajax_form(
    form_mock,
    client,
    admin,
    project,
    tag,
):
    form_mock.configure_mock(**{
        'return_value.return_value.is_valid.return_value': True,
        'return_value.return_value.save.return_value': [7, 23],
        'return_value.return_value.errors': [],
    })
    client.force_login(admin)
    url = reverse(
        'pontoon.admin.project.ajax.tag',
        kwargs=dict(
            project=project.slug,
            tag=tag.slug,
        ),
    )

    response = client.post(
        url,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert form_mock.return_value.return_value.is_valid.called
    assert form_mock.return_value.return_value.save.called
    assert (
        response.json()
        == {u'data': [7, 23]}
    )


@pytest.mark.django_db
@patch('pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form_class')
def test_view_project_tag_admin_ajax_form_bad(
    form_mock,
    client,
    admin,
    project,
    tag,
):
    form_mock.configure_mock(**{
        'return_value.return_value.is_valid.return_value': False,
        'return_value.return_value.errors': ['BIG PROBLEM'],
    })
    client.force_login(admin)
    url = reverse(
        'pontoon.admin.project.ajax.tag',
        kwargs=dict(
            project=project.slug,
            tag=tag.slug,
        ),
    )

    response = client.post(
        url,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 400
    assert form_mock.return_value.call_args[1]['project'] == project
    assert (
        dict(form_mock.return_value.call_args[1]['data'])
        == dict(tag=[u'tag'])
    )
    assert form_mock.return_value.return_value.is_valid.called
    assert not form_mock.return_value.return_value.save.called
    assert (
        response.json()
        == {u'errors': [u'BIG PROBLEM']}
    )

    form_mock.return_value.reset_mock()
    response = client.post(
        url,
        data=dict(foo='bar', bar='baz'),
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    assert response.status_code == 400
    assert form_mock.return_value.call_args[1]['project'] == project
    assert (
        dict(form_mock.return_value.call_args[1]['data'])
        == dict(
            foo=[u'bar'],
            bar=[u'baz'],
            tag=[u'tag'],
        )
    )
    assert form_mock.return_value.return_value.is_valid.called
    assert not form_mock.return_value.return_value.save.called
    assert (
        response.json()
        == {u'errors': [u'BIG PROBLEM']}
    )


@pytest.mark.django_db
@patch('pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form')
def test_view_project_tag_admin_ajax(form_mock, member, project, tag):
    form_mock.configure_mock(**{
        'return_value.save.return_value': 23,
    })
    url = reverse(
        'pontoon.admin.project.ajax.tag',
        kwargs=dict(
            project=project.slug,
            tag=tag.slug,
        ),
    )

    # no `get` here
    response = member.get(url)
    assert response.status_code == 404

    # need xhr headers
    response = member.post(url)
    assert response.status_code == 400

    # must be superuser!
    response = member.post(
        url,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    if not response.wsgi_request.user.is_superuser:
        assert not form_mock.called
        assert not form_mock.return_value.is_valid.called
        if response.wsgi_request.user.is_anonymous:
            assert response.status_code == 404
        else:
            assert response.status_code == 403
        return

    # Form.get_form was called
    assert form_mock.called
    assert form_mock.return_value.is_valid.called
    assert response.status_code == 200
    assert response.json() == {u'data': 23}


@pytest.mark.django_db
def test_view_project_tag_locales(client, project, tag):
    url = reverse(
        'pontoon.tags.project.tag',
        kwargs=dict(project=project.slug, tag=tag.slug),
    )

    # tag is not associated with project
    response = client.get(url)
    assert response.status_code == 404

    # tag has no priority so still wont show up...
    project.tag_set.add(tag)
    response = client.get(url)
    assert response.status_code == 404

    tag.priority = 3
    tag.save()
    response = client.get(url)
    assert response.status_code == 200

    # the response is not json
    with pytest.raises(ValueError):
        response.json()

    assert response.template_name == ['tags/tag.html']
    assert response.context_data['project'] == project

    res_tag = response.context_data['tag']
    assert isinstance(res_tag, TagTool)
    assert res_tag.object == tag


@pytest.mark.django_db
def test_view_project_tag_locales_ajax(client, project, tag):
    url = reverse(
        'pontoon.tags.ajax.teams',
        kwargs=dict(project=project.slug, tag=tag.slug),
    )
    project.tag_set.add(tag)
    tag.priority = 3
    tag.save()
    response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    # the response is not json even with xhr headers
    with pytest.raises(ValueError):
        response.json()

    assert response.template_name == ['projects/includes/teams.html']
    assert response.context_data['project'] == project

    locales = project.project_locale.all()
    assert len(response.context_data['locales']) == locales.count()

    for i, locale in enumerate(locales):
        locale = response.context_data['locales'][i]
        assert isinstance(locale, TaggedLocale)
        assert locale.code == locales[i].locale.code
        assert locale.name == locales[i].locale.name


@pytest.mark.django_db
def test_view_project_tag_ajax(client, project, tag):
    url = reverse(
        'pontoon.projects.ajax.tags',
        kwargs=dict(slug=project.slug),
    )
    project.tag_set.add(tag)
    tag.priority = 3
    tag.save()

    response = client.get(url)
    assert response.status_code == 400

    response = client.get(
        url, HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )

    # response returns html
    with pytest.raises(ValueError):
        response.json()
    assert tag.name in response.content
    assert tag.slug in response.content
