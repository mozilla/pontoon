from django.core.exceptions import PermissionDenied
from django.http import Http404

from raygun4py.middleware.django import Provider


class RaygunExceptionMiddleware(Provider):
    def process_exception(self, request, exception):
        # Ignore non-failure exceptions. We don't need to be notified
        # of these.
        if not isinstance(exception, (Http404, PermissionDenied)):
            return (super(RaygunExceptionMiddleware, self)
                    .process_exception(request, exception))
