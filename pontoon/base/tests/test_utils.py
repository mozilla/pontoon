import json

from django_nose.tools import (assert_equal,
                               assert_false,
                               assert_is_none,
                               assert_true)

from nose.tools import assert_raises

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseGone
from django.http import QueryDict
from django.views.decorators.http import require_POST

from mock import MagicMock

from pontoon.base.tests import ProjectFactory, TestCase
from pontoon.base.models import Project
from pontoon.base.utils import extension_in, get_object_or_none, ajaxview


class UtilsTests(TestCase):
    def test_extension_in(self):
        assert_true(extension_in('filename.txt', ['bat', 'txt']))
        assert_true(extension_in('filename.biff', ['biff']))
        assert_true(extension_in('filename.tar.gz', ['gz']))

        assert_false(extension_in('filename.txt', ['png', 'jpg']))
        assert_false(extension_in('.dotfile', ['bat', 'txt']))

        # Unintuitive, but that's how splitext works.
        assert_false(extension_in('filename.tar.gz', ['tar.gz']))

    def test_get_object_or_none(self):
        project = ProjectFactory.create(slug='exists')
        assert_is_none(get_object_or_none(Project, slug='does-not-exist'))
        assert_equal(get_object_or_none(Project, slug='exists'), project)


class AjaxviewTests(TestCase):
    """
    Tests related to the ajaxview decorator.
    """

    def _mock_request(self, get_args=None, post_args=None, method=None):
        """
        Returns mock object used to test views.
        :param get_args:  arguments passed as a GET data.
        :param post_args: arguments passed as a POST data.
        :param method: method of the request, can be one of the http methods.
        :return: customized magicmock instance.
        """
        mock_request = MagicMock()
        mock_request.method = method or 'GET'
        mock_request.GET = QueryDict(get_args or '')
        mock_request.POST = QueryDict(post_args or '')
        return mock_request

    def assert_response(self, response, status_code=200, content=None, response_class=None):
        """
        Parametrized assert block in order to reduce amount of code and simplify logic.
        :param response: object of response from django.view
        :param status_code: HTTP code
        :param content: content to be returned by django.view
        :param response_class: response class returned by view
        """
        assert_true(isinstance(response, response_class or HttpResponse))
        assert_equal(response.status_code, status_code)
        assert_equal(response.content, content or '')

    def test_passing_arguments(self):
        @ajaxview(['arg1'])
        def mock_get_args(request, arg1):
            return arg1 + ' world!'

        @ajaxview(require_post_args=['arg1'])
        def mock_post_args(request, arg1):
            return arg1 + ' world!'

        # Passing arguments via GET
        response = mock_get_args(self._mock_request(get_args='arg1=Hello'))
        self.assert_response(response, content='Hello world!')

        # Passing arguments via POST
        response = mock_post_args(self._mock_request(post_args='arg1=Hello'))
        self.assert_response(response, content='Hello world!')

    def test_missing_argument(self):
        """
        View should return error if argument is missing
        """
        @ajaxview(['missing_arg'])
        def mock_missing_get_args(request, missing_arg):
            return 'Cant reach here!'

        @ajaxview(require_post_args=['missing_arg'])
        def mock_missing_post_args(request, missing_arg):
            return 'Cant reach here!'

        response = mock_missing_get_args(self._mock_request())
        self.assert_response(response, content='error')

        # Testing if we won't pass some random parameter.
        response = mock_missing_get_args(self._mock_request())
        self.assert_response(response, content='error')

    def test_is_not_ajax(self):
        """
        Requests that aren't ajax should receive error.
        """
        @ajaxview()
        def mock_non_ajax_view(request):
            return "Hello world!"

        mock_request = MagicMock()
        mock_request.is_ajax.return_value = False

        response = mock_non_ajax_view(mock_request)
        self.assert_response(response, status_code=400, content='Bad Request: Request must be AJAX', response_class=HttpResponseBadRequest)

    def test_custom_exception(self):
        """
        Custom exceptions should be propagated from view.
        """
        @ajaxview()
        def mock_exception_view(request):
            raise Exception('CustomException')

        assert_raises(Exception, mock_exception_view, self._mock_request(), 'CustomException')

    def test_object_does_not_exist(self):
        """
        If view raises an ObjectDoesNotExist exception, we should return error response.
        """
        @ajaxview()
        def mock_exception_view(request):
            raise ObjectDoesNotExist("Missing object")

        response = mock_exception_view(self._mock_request())
        self.assert_response(response, content='error')

    def test_return_string(self):
        """
        If view returns string, it should be rendered as a normal HttpResponse.
        """
        @ajaxview()
        def mock_return_string_view(request):
            return "Hello world!"

        response = mock_return_string_view(self._mock_request())
        self.assert_response(response, content='Hello world!')

    def test_return_custom_response(self):
        """
        ajaxview should pass any custom response from the view.
        """
        @ajaxview()
        def mock_custom_response_view(request):
            return HttpResponseGone('Resource is gone!')

        response = mock_custom_response_view(self._mock_request())
        self.assert_response(response, status_code=410, content='Resource is gone!', response_class=HttpResponseGone)

    def test_return_json(self):
        """
        If view returns tuple, list or dictionary, they should be returned as an normal JSON response.
        """
        @ajaxview()
        def mock_tuple_view(request):
            return ('element1', 'element2')

        @ajaxview()
        def mock_list_view(request):
            return ['item1', 'item2']

        @ajaxview()
        def mock_dict_view(request):
            return {'property1': 'value1', 'property2': 'value2'}

        def assert_json_response(view, request, return_val):
            response = view(request)

            json_data = json.loads(response.content)
            assert_true(isinstance(response, HttpResponse))
            assert_equal(response['Content-type'], 'application/json')
            assert_equal(response.status_code, 200)
            assert_equal(json_data, return_val)

        mock_request = self._mock_request()

        # Unfortunately, tuples will be always converted to lists from json.
        assert_json_response(mock_tuple_view, mock_request, ['element1', 'element2'])
        assert_json_response(mock_list_view, mock_request,['item1', 'item2'])
        assert_json_response(mock_dict_view, mock_request, {'property1': 'value1', 'property2': 'value2'})

    def test_other_decorators(self):
        """
        Ajaxview should interact with other decorators, we'll try to check some of these used
        in our code.
        """
        @require_POST
        @ajaxview()
        def mock_require_post_view(request):
            return 'post view'

        @require_POST
        @transaction.atomic
        @ajaxview()
        def mock_atomic_view(request):
            return 'atomic view'

        # Test if require_POST will return 405 because of lack of post data.
        response = mock_require_post_view(self._mock_request())
        self.assert_response(response, status_code=405, content='')

        # Test successfull scenario for require_POST.
        response = mock_require_post_view(self._mock_request(post_args='some_arg=1', method='POST'))
        self.assert_response(response, content='post view')

        response = mock_atomic_view(self._mock_request(method='POST'))
        self.assert_response(response, content='atomic view')