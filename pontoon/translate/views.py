from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.views.decorators.csrf import (
    csrf_exempt,
    ensure_csrf_cookie,
)

from pontoon.base.models import (
    Locale,
)

from pontoon.base.utils import get_project_or_redirect


@csrf_exempt
def catchall_dev(request, context=None):
    return render(request, "translate.html", context=context, using="jinja2")


@ensure_csrf_cookie
def catchall_prod(request, context=None):
    return render(request, "translate.html", context=context, using="jinja2")


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

    # Get user theme
    if request.user.is_authenticated:
        user_theme = request.user.profile.theme + "-theme"

    # Validate Project
    if project.lower() != "all-projects":
        project = get_project_or_redirect(
            project,
            "pontoon.translate",
            "project",
            request.user,
            locale=locale.code,
            resource=resource,
        )
        if isinstance(project, HttpResponseRedirect):
            return project

        # Validate ProjectLocale
        if locale not in project.locales.all():
            raise Http404

    context = {
        "locale": get_preferred_locale(request),
        "notifications": [],
        "user_theme": user_theme,
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
