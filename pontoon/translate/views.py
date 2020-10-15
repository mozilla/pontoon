import requests

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles.views import serve
from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.template import engines
from django.views.decorators.csrf import (
    csrf_exempt,
    ensure_csrf_cookie,
)

from pontoon.base.models import (
    Locale,
    Project,
)


def static_serve_dev(request, path):
    """Proxy missing static files to the webpack server.

    This view replaces django's static files serve view. When a file is
    missing from django's paths, then we make a proxy request to the
    webpack server to see if it's a front-end file.

    Note that to enable this view, you need to run your django with the
    nostatic option, like this::

    $ ./manage.py runserver --nostatic

    """
    try:
        # First try to load the file with django's regular serve view.
        return serve(request, path, insecure=True)
    except Http404:
        # If the file couldn't be found in django's static files, then we
        # try to proxy it to the webpack server.
        return catchall_dev(request)


@csrf_exempt
def catchall_dev(request, context=None):
    """Proxy HTTP requests to the frontend dev server in development.

    The implementation is very basic e.g. it doesn't handle HTTP headers.

    """
    # URL to the development webpack server, used to redirect front-end requests.
    UPSTREAM = "http://localhost:3000"

    # Redirect websocket requests directly to the webpack server.
    if request.META.get("HTTP_UPGRADE", "").lower() == "websocket":
        return http.HttpResponseRedirect(UPSTREAM + request.path)

    upstream_url = UPSTREAM + request.path
    method = request.META["REQUEST_METHOD"].lower()
    response = getattr(requests, method)(upstream_url, stream=True)
    content_type = response.headers.get("Content-Type")

    if content_type == "text/html; charset=UTF-8":
        return http.HttpResponse(
            content=(
                engines["jinja2"]
                .from_string(response.text)
                .render(request=request, context=context)
            ),
            status=response.status_code,
            reason=response.reason,
        )

    return http.StreamingHttpResponse(
        streaming_content=response.iter_content(2 ** 12),
        content_type=content_type,
        status=response.status_code,
        reason=response.reason,
    )


# For production, we've added the front-end static files to our list of
# static folders. We can thus simply return a template view of index.html.
@ensure_csrf_cookie
def catchall_prod(request, context=None):
    return render(request, "index.html", context=context, using="jinja2")


def get_preferred_locale(request):
    """Return the locale the current user prefers, if any.

    Used to decide in which language to show the Translate page.

    """
    user = request.user
    if user.is_authenticated and user.profile.custom_homepage:
        return user.profile.custom_homepage

    return None


def translate(request, locale, project, resource):
    # Validate Locale
    locale = get_object_or_404(Locale, code=locale)

    # Validate Project
    if project.lower() != "all-projects":
        project = get_object_or_404(
            Project.objects.visible_for(request.user).available(), slug=project
        )

        # Validate ProjectLocale
        if locale not in project.locales.all():
            raise Http404

    context = {
        "locale": get_preferred_locale(request),
        "notifications": [],
    }

    # Get system notifications and pass them down. We need to transform the
    # django object so that it can be turned into JSON.
    notifications = messages.get_messages(request)
    if notifications:
        context["notifications"] = [
            {"content": str(x), "type": x.tags} for x in notifications
        ]

    if settings.DEBUG:
        return catchall_dev(request, context=context)

    return catchall_prod(request, context=context)
