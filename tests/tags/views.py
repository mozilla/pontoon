
import pytest

from mock import MagicMock, PropertyMock, patch

from django.urls import reverse


@pytest.mark.django_db
def test_view_project_tag_admin_ajax_form(client, admin0, project0, tag0):
    client.force_login(admin0)
    url = reverse(
        'pontoon.admin.project.ajax.tag',
        kwargs=dict(
            project=project0.slug,
            tag=tag0.slug))
    _patch_ctx = patch(
        'pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form_class')

    with _patch_ctx as m:
        form_m = MagicMock()
        form_m.is_valid.return_value = True
        form_m.save.return_value = [7, 23]
        errors_p = PropertyMock(return_value=[])
        type(form_m).errors = errors_p
        form_class_m = MagicMock(return_value=form_m)
        m.return_value = form_class_m
        response = client.post(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert form_m.is_valid.called
        assert form_m.save.called
        assert (
            response.json()
            == {u'data': [7, 23]})


@pytest.mark.django_db
def test_view_project_tag_admin_ajax_form_bad(client, admin0, project0, tag0):
    client.force_login(admin0)
    url = reverse(
        'pontoon.admin.project.ajax.tag',
        kwargs=dict(
            project=project0.slug,
            tag=tag0.slug))
    _patch_ctx = patch(
        'pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form_class')

    with _patch_ctx as m:
        form_m = MagicMock()
        form_m.is_valid.return_value = False
        errors_p = PropertyMock(return_value=['BIG PROBLEM'])
        type(form_m).errors = errors_p
        form_class_m = MagicMock(return_value=form_m)
        m.return_value = form_class_m
        response = client.post(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 400
        assert form_class_m.call_args[1]['project'] == project0
        assert (
            dict(form_class_m.call_args[1]['data'])
            == dict(
                tag=[u'tag0']))
        assert form_m.is_valid.called
        assert not form_m.save.called
        assert (
            response.json()
            == {u'errors': [u'BIG PROBLEM']})

        form_class_m.reset_mock()
        response = client.post(
            url,
            data=dict(foo='bar', bar='baz'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 400
        assert form_class_m.call_args[1]['project'] == project0
        assert (
            dict(form_class_m.call_args[1]['data'])
            == dict(
                foo=[u'bar'],
                bar=[u'baz'],
                tag=[u'tag0']))
        assert form_m.is_valid.called
        assert not form_m.save.called
        assert (
            response.json()
            == {u'errors': [u'BIG PROBLEM']})


@pytest.mark.django_db
def test_view_project_tag_admin_ajax(clients, project0, tag0):
    url = reverse(
        'pontoon.admin.project.ajax.tag',
        kwargs=dict(
            project=project0.slug,
            tag=tag0.slug))
    form_m = MagicMock()
    _patch_ctx = patch(
        'pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form')

    with _patch_ctx as m:
        m.return_value = form_m
        form_m.save.return_value = 23

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
            assert not m.called
            assert not form_m.is_valid.called
            if response.wsgi_request.user.is_anonymous:
                assert response.status_code == 404
            else:
                assert response.status_code == 403
            return
        assert m.called
        assert form_m.is_valid.called
        assert response.status_code == 200
