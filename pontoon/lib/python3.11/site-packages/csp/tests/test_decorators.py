from django.http import HttpResponse
from django.test import RequestFactory
from django.test.utils import override_settings

from csp.decorators import csp, csp_exempt, csp_replace, csp_update
from csp.middleware import CSPMiddleware
from csp.tests.utils import response

REQUEST = RequestFactory().get("/")
mw = CSPMiddleware(response())


def test_csp_exempt():
    @csp_exempt
    def view(request):
        return HttpResponse()

    response = view(REQUEST)
    assert response._csp_exempt


@override_settings(CSP_IMG_SRC=["foo.com"])
def test_csp_update():
    def view_without_decorator(request):
        return HttpResponse()

    response = view_without_decorator(REQUEST)
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["default-src 'self'", "img-src foo.com"]

    @csp_update(IMG_SRC="bar.com")
    def view_with_decorator(request):
        return HttpResponse()

    response = view_with_decorator(REQUEST)
    assert response._csp_update == {"img-src": "bar.com"}
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["default-src 'self'", "img-src foo.com bar.com"]

    response = view_without_decorator(REQUEST)
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["default-src 'self'", "img-src foo.com"]


@override_settings(CSP_IMG_SRC=["foo.com"])
def test_csp_replace():
    def view_without_decorator(request):
        return HttpResponse()

    response = view_without_decorator(REQUEST)
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["default-src 'self'", "img-src foo.com"]

    @csp_replace(IMG_SRC="bar.com")
    def view_with_decorator(request):
        return HttpResponse()

    response = view_with_decorator(REQUEST)
    assert response._csp_replace == {"img-src": "bar.com"}
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["default-src 'self'", "img-src bar.com"]

    response = view_without_decorator(REQUEST)
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["default-src 'self'", "img-src foo.com"]

    @csp_replace(IMG_SRC=None)
    def view_removing_directive(request):
        return HttpResponse()

    response = view_removing_directive(REQUEST)
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["default-src 'self'"]


def test_csp():
    def view_without_decorator(request):
        return HttpResponse()

    response = view_without_decorator(REQUEST)
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["default-src 'self'"]

    @csp(IMG_SRC=["foo.com"], FONT_SRC=["bar.com"])
    def view_with_decorator(request):
        return HttpResponse()

    response = view_with_decorator(REQUEST)
    assert response._csp_config == {"img-src": ["foo.com"], "font-src": ["bar.com"]}
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["font-src bar.com", "img-src foo.com"]

    response = view_without_decorator(REQUEST)
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["default-src 'self'"]


def test_csp_string_values():
    # Test backwards compatibility where values were strings
    @csp(IMG_SRC="foo.com", FONT_SRC="bar.com")
    def view_with_decorator(request):
        return HttpResponse()

    response = view_with_decorator(REQUEST)
    assert response._csp_config == {"img-src": ["foo.com"], "font-src": ["bar.com"]}
    mw.process_response(REQUEST, response)
    policy_list = sorted(response["Content-Security-Policy"].split("; "))
    assert policy_list == ["font-src bar.com", "img-src foo.com"]
