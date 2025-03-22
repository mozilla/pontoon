from django.http import HttpResponse
from django.test import RequestFactory
from django.test.utils import override_settings

from csp.contrib.rate_limiting import RateLimitedCSPMiddleware
from csp.tests.utils import response

HEADER = "Content-Security-Policy"
mw = RateLimitedCSPMiddleware(response())
rf = RequestFactory()


@override_settings(CSP_REPORT_PERCENTAGE=0.1, CSP_REPORT_URI="x")
def test_report_percentage():
    times_seen = 0
    for _ in range(5000):
        request = rf.get("/")
        response = HttpResponse()
        mw.process_response(request, response)
        if "report-uri" in response[HEADER]:
            times_seen += 1
    # Roughly 10%
    assert 400 <= times_seen <= 600
