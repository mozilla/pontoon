from unittest.mock import patch

import pytest

from django.urls import reverse


@pytest.mark.django_db
@patch("pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form_class")
def test_view_project_tag_admin_ajax_form(
    form_mock,
    client,
    admin,
    project_a,
    tag_a,
):
    form_mock.configure_mock(
        **{
            "return_value.return_value.is_valid.return_value": True,
            "return_value.return_value.save.return_value": [7, 23],
            "return_value.return_value.errors": [],
        }
    )
    client.force_login(admin)
    url = reverse(
        "pontoon.admin.project.ajax.tag",
        kwargs=dict(
            project=project_a.slug,
            tag=tag_a.slug,
        ),
    )

    response = client.post(
        url,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert form_mock.return_value.return_value.is_valid.called
    assert form_mock.return_value.return_value.save.called
    assert response.json() == {"data": [7, 23]}


@pytest.mark.django_db
@patch("pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form_class")
def test_view_project_tag_admin_ajax_form_bad(
    form_mock,
    client,
    admin,
    project_a,
    tag_a,
):
    form_mock.configure_mock(
        **{
            "return_value.return_value.is_valid.return_value": False,
            "return_value.return_value.errors": ["BIG PROBLEM"],
        }
    )
    client.force_login(admin)
    url = reverse(
        "pontoon.admin.project.ajax.tag",
        kwargs=dict(
            project=project_a.slug,
            tag=tag_a.slug,
        ),
    )

    response = client.post(
        url,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 400
    assert form_mock.return_value.call_args[1]["project"] == project_a
    assert dict(form_mock.return_value.call_args[1]["data"]) == dict(tag=["tag"])
    assert form_mock.return_value.return_value.is_valid.called
    assert not form_mock.return_value.return_value.save.called
    assert response.json() == {"errors": ["BIG PROBLEM"]}

    form_mock.return_value.reset_mock()
    response = client.post(
        url,
        data=dict(foo="bar", bar="baz"),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 400
    assert form_mock.return_value.call_args[1]["project"] == project_a
    assert dict(form_mock.return_value.call_args[1]["data"]) == dict(
        foo=["bar"],
        bar=["baz"],
        tag=["tag"],
    )
    assert form_mock.return_value.return_value.is_valid.called
    assert not form_mock.return_value.return_value.save.called
    assert response.json() == {"errors": ["BIG PROBLEM"]}


@pytest.mark.django_db
@patch("pontoon.tags.admin.views.ProjectTagAdminAjaxView.get_form")
def test_view_project_tag_admin_ajax(form_mock, member, project_a, tag_a):
    form_mock.configure_mock(**{"return_value.save.return_value": 23})
    url = reverse(
        "pontoon.admin.project.ajax.tag",
        kwargs=dict(
            project=project_a.slug,
            tag=tag_a.slug,
        ),
    )

    # no `get` here
    response = member.client.get(url)
    assert response.status_code == 404

    # need xhr headers
    response = member.client.post(url)
    assert response.status_code == 400

    # must be superuser!
    response = member.client.post(
        url,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
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
    assert response.json() == {"data": 23}
