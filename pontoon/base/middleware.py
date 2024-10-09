import logging
import time

from ipaddress import ip_address

from raygun4py.middleware.django import Provider

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from pontoon.base.utils import is_ajax


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

        # Convert request IP string to an IP object, check if it belongs to an
        # IP range
        try:
            ip_obj = ip_address(ip)
        except ValueError:
            log = logging.getLogger(__name__)
            log.error(f"Invalid IP detected in BlockedIpMiddleware: {ip}")
            return None

        for ip_range in settings.BLOCKED_IP_RANGES:
            if ip_obj in ip_range:
                return HttpResponseForbidden("<h1>Forbidden</h1>")

        return None


class EmailConsentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not settings.EMAIL_CONSENT_ENABLED:
            return response

        if not request.user.is_authenticated:
            return response

        if request.user.profile.email_consent_dismissed_at is not None:
            return response

        if is_ajax(request):
            return response

        email_consent_url = "pontoon.messaging.email_consent"
        if request.path == reverse(email_consent_url):
            return response

        request.session["next_path"] = request.get_full_path()
        return redirect(email_consent_url)


class ThrottleIpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_count = settings.THROTTLE_MAX_COUNT
        self.period = settings.THROTTLE_PERIOD
        self.block_duration = settings.THROTTLE_BLOCK_DURATION

    def __call__(self, request):
        # Get the client's IP address
        try:
            ip = request.META["HTTP_X_FORWARDED_FOR"]
            # If comma-separated list of IPs, take just the last one
            # http://stackoverflow.com/a/18517550
            ip = ip.split(",")[-1]
        except KeyError:
            ip = request.META["REMOTE_ADDR"]

        ip = ip.strip()

        # Generate cache keys
        throttle_key = f"throttle_ip_{ip}"
        blocked_key = f"blocked_ip_{ip}"

        # Check if IP is currently blocked
        if cache.get(blocked_key):
            return JsonResponse({"detail": "Too Many Requests"}, status=429)

        # Fetch current request count and timestamp
        request_data = cache.get(throttle_key)
        now = time.time()

        if request_data:
            request_count, first_request_time = request_data
            if request_count >= self.max_count:
                # Block further requests for block_duration seconds
                cache.set(blocked_key, True, self.block_duration)
                return JsonResponse({"detail": "Too Many Requests"}, status=429)
            else:
                # Increment the request count and update cache
                cache.set(
                    throttle_key, (request_count + 1, first_request_time), self.period
                )
        else:
            # Reset the count and timestamp if first request in the period
            cache.set(throttle_key, (1, now), self.period)

        response = self.get_response(request)
        return response
