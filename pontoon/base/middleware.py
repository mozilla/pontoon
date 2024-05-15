from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from pontoon.base.utils import is_ajax
from raygun4py.middleware.django import Provider


class RaygunExceptionMiddleware(Provider, MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self._async_check()

    def process_exception(self, request, exception):
        # Ignore non-failure exceptions. We don't need to be notified
        # of these.
        if not isinstance(exception, (Http404, PermissionDenied)):
            return super().process_exception(request, exception)


class BlockedIpMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            ip = request.META["HTTP_X_FORWARDED_FOR"]
            # If comma-separated list of IPs, take just the last one
            # http://stackoverflow.com/a/18517550
            ip = ip.split(",")[-1]
        except KeyError:
            ip = request.META["REMOTE_ADDR"]

        ip = ip.strip()

        # Block client IP addresses via settings variable BLOCKED_IPS
        if ip in settings.BLOCKED_IPS:
            return HttpResponseForbidden("<h1>Forbidden</h1>")

        return None


class EmailConsentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not settings.EMAIL_CONSENT_ENABLED:
            return None

        if not request.user.is_authenticated:
            return None

        if request.user.profile.email_consent_dismissed_at is not None:
            return None

        if is_ajax(request):
            return None

        email_consent_url = "pontoon.messaging.email_consent"
        if request.path == reverse(email_consent_url):
            return None

        request.session["next_path"] = request.get_full_path()
        return redirect(email_consent_url)
