from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden
from raygun4py.middleware.django import Provider


class HerokuDemoSetupMiddleware(object):
    """
    Forces user to setup demo instance during the initial state.
    There's a chance that user will try to open newly created instance by
    typing an url in the browser window. That's why we have to ensure
    that setup view is called as the first view.
    """
    def process_request(self, request):
        path = request.path
        current_domain = Site.objects.get(pk=1).domain

        if settings.HEROKU_DEMO and path != '/heroku-setup/' and current_domain == 'example.com':
            return redirect('pontoon.heroku_setup')


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

        ip = ip.strip()

        # Block client IP addresses via settings variable BLOCKED_IPS
        if ip in settings.BLOCKED_IPS:
            return HttpResponseForbidden('<h1>Forbidden</h1>')

        return None
