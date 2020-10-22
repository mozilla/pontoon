import json
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from django.http import Http404

from pontoon.base.views import AjaxFormView, AjaxFormPostView


def test_view_ajax_form(rf):
    with patch("pontoon.base.views.AjaxFormView.get_form") as form_m, patch(
        "pontoon.base.views.AjaxFormView.render_to_response"
    ) as response_m:
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
    with patch("pontoon.base.views.AjaxFormPostView.get_form") as form_m, patch(
        "pontoon.base.views.AjaxFormPostView.render_to_response"
    ):
        with pytest.raises(Http404):
            AjaxFormPostView.as_view()(rf.get("/foo/bar"))
        with pytest.raises(Http404):
            AjaxFormPostView.as_view()(
                rf.get("/foo/bar", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            )
        assert not form_m.called


def test_view_ajax_form_submit_bad(rf):
    with patch("pontoon.base.views.AjaxFormView.get_form") as form_m, patch(
        "pontoon.base.views.AjaxFormView.render_to_response"
    ) as response_m:
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
    with patch("pontoon.base.views.AjaxFormView.get_form") as form_m, patch(
        "pontoon.base.views.AjaxFormView.render_to_response"
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
