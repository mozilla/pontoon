import logging
import time

from ipaddress import ip_address

from raygun4py.middleware.django import Provider

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from pontoon.base.utils import get_ip, is_ajax


log = logging.getLogger(__name__)


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
        ip = get_ip(request)

        # Block client IP addresses via settings variable BLOCKED_IPS
        if ip in settings.BLOCKED_IPS:
            return HttpResponseForbidden("<h1>Forbidden</h1>")

        # Convert request IP string to an IP object, check if it belongs to an
        # IP range
        try:
            ip_obj = ip_address(ip)
        except ValueError:
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
        self.observation_period = settings.THROTTLE_OBSERVATION_PERIOD
        self.block_duration = settings.THROTTLE_BLOCK_DURATION

        # Set to block_duration if longer, otherwise requests will be blocked until
        # the observation_period expires rather than when the block_duration expires
        if self.observation_period > self.block_duration:
            self.observation_period = self.block_duration

    def _throttle(self, request):
        response = render(request, "429.html", status=429)
        response["Retry-After"] = self.block_duration
        return response

    def __call__(self, request):
        if settings.THROTTLE_ENABLED is False:
            return self.get_response(request)

        ip = get_ip(request)

        # Generate cache keys
        observed_key = f"observed_ip_{ip}"
        blocked_key = f"blocked_ip_{ip}"

        # Check if IP is currently blocked
        if cache.get(blocked_key):
            return self._throttle(request)

        # Fetch current request count and timestamp
        request_data = cache.get(observed_key)
        now = time.time()

        if request_data:
            request_count, first_request_time = request_data
            if request_count >= self.max_count:
                # Block further requests for block_duration seconds
                cache.set(blocked_key, True, self.block_duration)
                log.error(f"Blocked IP {ip} for {self.block_duration} seconds")
                return self._throttle(request)
            else:
                # Increment the request count and update cache
                cache.set(
                    observed_key,
                    (request_count + 1, first_request_time),
                    self.observation_period,
                )
        else:
            # Reset the count and timestamp if first request in the period
            cache.set(observed_key, (1, now), self.observation_period)

        response = self.get_response(request)
        return response
