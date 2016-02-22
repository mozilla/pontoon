from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden

from raygun4py.middleware.django import Provider


class RaygunExceptionMiddleware(Provider):
    def process_exception(self, request, exception):
        # Ignore non-failure exceptions. We don't need to be notified
        # of these.
        if not isinstance(exception, (Http404, PermissionDenied)):
            return (super(RaygunExceptionMiddleware, self)
                    .process_exception(request, exception))


class BlockedIpMiddleware(object):
    def process_request(self, request):
        # Block IP addresses via settings variable BLOCKED_IPS
        if request.META['REMOTE_ADDR'] in settings.BLOCKED_IPS:
            return HttpResponseForbidden('<h1>Forbidden</h1>')
        return None
