from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
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
        try:
            ip = request.META['HTTP_X_FORWARDED_FOR']
            # If comma-separated list of IPs, take just the last one
            # http://stackoverflow.com/a/18517550
            ip = ip.split(',')[-1]
        except KeyError:
            ip = request.META['REMOTE_ADDR']

        # Block client IP addresses via settings variable BLOCKED_IPS
        if ip in settings.BLOCKED_IPS:
            return HttpResponseForbidden('<h1>Forbidden</h1>')

        return None


class PersonaMigrationMiddleware(object):
    """
    Middleware that redirects a user to the migration page until an account is
    fully migrated into firefox accounts.
    """

    def process_request(self, request):
        if not request.user.is_authenticated():
            return None

        sign_in_migration_url = reverse('pontoon.sign-in-migration')

        if not request.user.logged_via('fxa') and request.path != sign_in_migration_url\
                and not request.path.startswith('/accounts/'):
            return redirect(sign_in_migration_url)
