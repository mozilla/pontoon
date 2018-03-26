
import pytest

from mock import patch

from django.urls import reverse

from pontoon.tags.utils import TaggedLocale, TagTool


@pytest.mark.django_db
@patch('pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form_class')
def test_view_project_tag_admin_ajax_form(form_mock, client, admin0,
                                          project0, tag0):
    form_mock.configure_mock(
        **{'return_value.return_value.is_valid.return_value': True,
           'return_value.return_value.save.return_value': [7, 23],
           'return_value.return_value.errors': []})
    client.force_login(admin0)
    url = reverse(
        'pontoon.admin.project.ajax.tag',
        kwargs=dict(
            project=project0.slug,
            tag=tag0.slug))

    response = client.post(
        url,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert form_mock.return_value.return_value.is_valid.called
    assert form_mock.return_value.return_value.save.called
    assert (
        response.json()
        == {u'data': [7, 23]})


@pytest.mark.django_db
@patch('pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form_class')
def test_view_project_tag_admin_ajax_form_bad(form_mock, client, admin0,
                                              project0, tag0):
    form_mock.configure_mock(
        **{'return_value.return_value.is_valid.return_value': False,
           'return_value.return_value.errors': ['BIG PROBLEM']})
    client.force_login(admin0)
    url = reverse(
        'pontoon.admin.project.ajax.tag',
        kwargs=dict(
            project=project0.slug,
            tag=tag0.slug))

    response = client.post(
        url,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 400
    assert form_mock.return_value.call_args[1]['project'] == project0
    assert (
        dict(form_mock.return_value.call_args[1]['data'])
        == dict(tag=[u'tag0']))
    assert form_mock.return_value.return_value.is_valid.called
    assert not form_mock.return_value.return_value.save.called
    assert (
        response.json()
        == {u'errors': [u'BIG PROBLEM']})

    form_mock.return_value.reset_mock()
    response = client.post(
        url,
        data=dict(foo='bar', bar='baz'),
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 400
    assert form_mock.return_value.call_args[1]['project'] == project0
    assert (
        dict(form_mock.return_value.call_args[1]['data'])
        == dict(
            foo=[u'bar'],
            bar=[u'baz'],
            tag=[u'tag0']))
    assert form_mock.return_value.return_value.is_valid.called
    assert not form_mock.return_value.return_value.save.called
    assert (
        response.json()
        == {u'errors': [u'BIG PROBLEM']})


@pytest.mark.django_db
@patch('pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form')
def test_view_project_tag_admin_ajax(form_mock, clients, project0, tag0):
    form_mock.configure_mock(
        **{'return_value.save.return_value': 23})
    url = reverse(
        'pontoon.admin.project.ajax.tag',
        kwargs=dict(
            project=project0.slug,
            tag=tag0.slug))

    # no `get` here
    response = clients.get(url)
    assert response.status_code == 404

    # need xhr headers
    response = clients.post(url)
    assert response.status_code == 400

    # must be superuser!
    response = clients.post(
        url,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
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
def test_view_project_tag_locales(client, project0, tag0):
    url = reverse(
        'pontoon.tags.project.tag',
        kwargs=dict(project=project0.slug, tag=tag0.slug))

    # tag is not associated with project
    response = client.get(url)
    assert response.status_code == 404

    # tag has no priority so still wont show up...
    project0.tag_set.add(tag0)
    response = client.get(url)
    assert response.status_code == 404

    tag0.priority = 3
    tag0.save()
    response = client.get(url)
    assert response.status_code == 200

    # the response is not json
    with pytest.raises(ValueError):
        response.json()

    assert response.template_name == ['tags/tag.html']
    assert response.context_data['project'] == project0

    tag = response.context_data['tag']
    assert isinstance(tag, TagTool)
    assert tag.object == tag0


@pytest.mark.django_db
def test_view_project_tag_locales_ajax(client, project0, tag0):
    url = reverse(
        'pontoon.tags.ajax.teams',
        kwargs=dict(project=project0.slug, tag=tag0.slug))
    project0.tag_set.add(tag0)
    tag0.priority = 3
    tag0.save()
    response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    # the response is not json even with xhr headers
    with pytest.raises(ValueError):
        response.json()

    assert response.template_name == ['projects/includes/teams.html']
    assert response.context_data['project'] == project0

    locales = project0.project_locale.all()
    assert len(response.context_data['locales']) == locales.count()

    for i, locale in enumerate(locales):
        locale = response.context_data['locales'][i]
        assert isinstance(locale, TaggedLocale)
        assert locale.code == locales[i].locale.code
        assert locale.name == locales[i].locale.name


@pytest.mark.django_db
def test_view_project_tag_ajax(client, project0, tag0):
    url = reverse(
        'pontoon.projects.ajax.tags',
        kwargs=dict(slug=project0.slug))
    project0.tag_set.add(tag0)
    tag0.priority = 3
    tag0.save()

    response = client.get(url)
    assert response.status_code == 400

    response = client.get(
        url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    # response returns html
    with pytest.raises(ValueError):
        response.json()
    assert tag0.name in response.content
    assert tag0.slug in response.content
