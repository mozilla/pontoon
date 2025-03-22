import random

from django.conf import settings

from csp.middleware import CSPMiddleware
from csp.utils import build_policy


class RateLimitedCSPMiddleware(CSPMiddleware):
    """A CSP middleware that rate-limits the number of violation reports sent
    to report-uri by excluding it from some requests."""

    def build_policy(self, request, response):
        config = getattr(response, "_csp_config", None)
        update = getattr(response, "_csp_update", None)
        replace = getattr(response, "_csp_replace", {})
        nonce = getattr(request, "_csp_nonce", None)

        report_percentage = getattr(settings, "CSP_REPORT_PERCENTAGE")
        include_report_uri = random.random() < report_percentage
        if not include_report_uri:
            replace["report-uri"] = None

        return build_policy(config=config, update=update, replace=replace, nonce=nonce)
