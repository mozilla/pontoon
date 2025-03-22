from django.http import HttpResponse
from django.test import RequestFactory

from csp.context_processors import nonce
from csp.middleware import CSPMiddleware
from csp.tests.utils import response

rf = RequestFactory()
mw = CSPMiddleware(response())


def test_nonce_context_processor():
    request = rf.get("/")
    mw.process_request(request)
    context = nonce(request)

    response = HttpResponse()
    mw.process_response(request, response)

    assert context["CSP_NONCE"] == request.csp_nonce


def test_nonce_context_processor_with_middleware_disabled():
    request = rf.get("/")
    context = nonce(request)

    assert context["CSP_NONCE"] == ""
