from __future__ import absolute_import, unicode_literals

import sys

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden
from raygun4py.middleware.django import Provider
from six import text_type


class RaygunExceptionMiddleware(Provider):
    def process_exception(self, request, exception):
        # Ignore non-failure exceptions. We don't need to be notified
        # of these.
        if not isinstance(exception, (Http404, PermissionDenied)):
            # On Python 2, Raygun4py fails to send an exception with the Unicode message
            # and throws the UnicodeDecodeError.
            # To avoid this, the middleware casts the exception to the str object.
            # On Python 3, Raygun4py requires an instance of an Exception instead of a string.
            # This is the temporary solution and will be removed after the migration to Python 3.
            # Ref: https://bugzilla.mozilla.org/show_bug.cgi?id=1600344
            if sys.version_info.major == 2:
                exc_value = text_type(exception).encode('utf-8')
            else:
                exc_value = exception
            return super(RaygunExceptionMiddleware, self).process_exception(request, exc_value)


class BlockedIpMiddleware(object):
    def process_request(self, request):
        try:
            ip = request.META['HTTP_X_FORWARDED_FOR']
            # If comma-separated list of IPs, take just the last one
            # http://stackoverflow.com/a/18517550
            ip = ip.split(',')[-1]
        except KeyError:
            ip = request.META['REMOTE_ADDR']

        ip = ip.strip()

        # Block client IP addresses via settings variable BLOCKED_IPS
        if ip in settings.BLOCKED_IPS:
            return HttpResponseForbidden('<h1>Forbidden</h1>')

        return None


class AutomaticLoginUserMiddleware(object):
    """
    This middleware automatically logs in the user specified for AUTO_LOGIN.
    """

    def process_request(self, request):
        if settings.AUTO_LOGIN and not request.user.is_authenticated():
            user = auth.authenticate(
                username=settings.AUTO_LOGIN_USERNAME,
                password=settings.AUTO_LOGIN_PASSWORD
            )

            if user:
                request.user = user
                auth.login(request, user)
