from django.conf import settings
from django.contrib import messages
from django.http import Http404
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
    Project,
)

from pontoon.base.utils import handle_old_slug_redirect


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


@handle_old_slug_redirect("pontoon.translate")
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
