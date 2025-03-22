import base64
import http.client as http_client
import os
from functools import partial

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from csp.utils import build_policy


class CSPMiddleware(MiddlewareMixin):
    """
    Implements the Content-Security-Policy response header, which
    conforming user-agents can use to restrict the permitted sources
    of various content.

    See http://www.w3.org/TR/CSP/

    """

    def _make_nonce(self, request):
        # Ensure that any subsequent calls to request.csp_nonce return the
        # same value
        if not getattr(request, "_csp_nonce", None):
            request._csp_nonce = base64.b64encode(os.urandom(16)).decode("ascii")
        return request._csp_nonce

    def process_request(self, request):
        nonce = partial(self._make_nonce, request)
        request.csp_nonce = SimpleLazyObject(nonce)

    def process_response(self, request, response):
        if getattr(response, "_csp_exempt", False):
            return response

        # Check for ignored path prefix.
        prefixes = getattr(settings, "CSP_EXCLUDE_URL_PREFIXES", ())
        if request.path_info.startswith(prefixes):
            return response

        # Check for debug view
        status_code = response.status_code
        exempted_debug_codes = (
            http_client.INTERNAL_SERVER_ERROR,
            http_client.NOT_FOUND,
        )
        if status_code in exempted_debug_codes and settings.DEBUG:
            return response

        header = "Content-Security-Policy"
        if getattr(settings, "CSP_REPORT_ONLY", False):
            header += "-Report-Only"

        if header in response:
            # Don't overwrite existing headers.
            return response

        response[header] = self.build_policy(request, response)

        return response

    def build_policy(self, request, response):
        config = getattr(response, "_csp_config", None)
        update = getattr(response, "_csp_update", None)
        replace = getattr(response, "_csp_replace", None)
        nonce = getattr(request, "_csp_nonce", None)
        return build_policy(config=config, update=update, replace=replace, nonce=nonce)
