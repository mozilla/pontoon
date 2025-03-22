from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from django.test import RequestFactory
from django.test.utils import override_settings

from csp.middleware import CSPMiddleware
from csp.tests.utils import response

HEADER = "Content-Security-Policy"
mw = CSPMiddleware(response())
rf = RequestFactory()


def test_add_header():
    request = rf.get("/")
    response = HttpResponse()
    mw.process_response(request, response)
    assert HEADER in response


def test_exempt():
    request = rf.get("/")
    response = HttpResponse()
    response._csp_exempt = True
    mw.process_response(request, response)
    assert HEADER not in response


@override_settings(CSP_EXCLUDE_URL_PREFIXES=("/inlines-r-us"))
def text_exclude():
    request = rf.get("/inlines-r-us/foo")
    response = HttpResponse()
    mw.process_response(request, response)
    assert HEADER not in response


@override_settings(CSP_REPORT_ONLY=True)
def test_report_only():
    request = rf.get("/")
    response = HttpResponse()
    mw.process_response(request, response)
    assert HEADER not in response
    assert HEADER + "-Report-Only" in response


def test_dont_replace():
    request = rf.get("/")
    response = HttpResponse()
    response[HEADER] = "default-src example.com"
    mw.process_response(request, response)
    assert response[HEADER] == "default-src example.com"


def test_use_config():
    request = rf.get("/")
    response = HttpResponse()
    response._csp_config = {"default-src": ["example.com"]}
    mw.process_response(request, response)
    assert response[HEADER] == "default-src example.com"


def test_use_update():
    request = rf.get("/")
    response = HttpResponse()
    response._csp_update = {"default-src": ["example.com"]}
    mw.process_response(request, response)
    assert response[HEADER] == "default-src 'self' example.com"


@override_settings(CSP_IMG_SRC=["foo.com"])
def test_use_replace():
    request = rf.get("/")
    response = HttpResponse()
    response._csp_replace = {"img-src": ["bar.com"]}
    mw.process_response(request, response)
    policy_list = sorted(response[HEADER].split("; "))
    assert policy_list == ["default-src 'self'", "img-src bar.com"]


@override_settings(DEBUG=True)
def test_debug_errors_exempt():
    request = rf.get("/")
    response = HttpResponseServerError()
    mw.process_response(request, response)
    assert HEADER not in response


@override_settings(DEBUG=True)
def test_debug_notfound_exempt():
    request = rf.get("/")
    response = HttpResponseNotFound()
    mw.process_response(request, response)
    assert HEADER not in response


def test_nonce_created_when_accessed():
    request = rf.get("/")
    mw.process_request(request)
    nonce = str(request.csp_nonce)
    response = HttpResponse()
    mw.process_response(request, response)
    assert nonce in response[HEADER]


def test_no_nonce_when_not_accessed():
    request = rf.get("/")
    mw.process_request(request)
    response = HttpResponse()
    mw.process_response(request, response)
    assert "nonce-" not in response[HEADER]


def test_nonce_regenerated_on_new_request():
    request1 = rf.get("/")
    request2 = rf.get("/")
    mw.process_request(request1)
    mw.process_request(request2)
    nonce1 = str(request1.csp_nonce)
    nonce2 = str(request2.csp_nonce)
    assert request1.csp_nonce != request2.csp_nonce

    response1 = HttpResponse()
    response2 = HttpResponse()
    mw.process_response(request1, response1)
    mw.process_response(request2, response2)
    assert nonce1 not in response2[HEADER]
    assert nonce2 not in response1[HEADER]


@override_settings(CSP_INCLUDE_NONCE_IN=[])
def test_no_nonce_when_disabled_by_settings():
    request = rf.get("/")
    mw.process_request(request)
    nonce = str(request.csp_nonce)
    response = HttpResponse()
    mw.process_response(request, response)
    assert nonce not in response[HEADER]
