from django.db.models import Count
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template import Context, Template
from django.urls import reverse

from pontoon.base.models import Locale, User
from pontoon.base.models.translation import Translation
from pontoon.base.services import get_locale_or_redirect
from pontoon.base.utils import get_project_locale_from_request
from pontoon.homepage.models import Homepage


def homepage(request) -> HttpResponse:
    user: User = request.user

    # Redirect user to the selected home page or '/'.
    if user.is_authenticated and (profile := user.profile).custom_homepage != "":
        # If custom homepage not set yet, set it to the most contributed locale team page
        if profile.custom_homepage is None:
            top_locale = _top_contributed_locale(user)
            if top_locale:
                profile.custom_homepage = top_locale
                profile.save(update_fields=["custom_homepage"])

        if profile.custom_homepage:
            try:
                # Call to get_locale_or_redirect to check if the custom homepage locale exists
                get_locale_or_redirect(profile.custom_homepage)
                return redirect("pontoon.teams.team", locale=profile.custom_homepage)
            except Http404:
                pass

    # Guess user's team page or redirect to /teams
    locale = get_project_locale_from_request(request, Locale.objects.available())
    if locale not in ("en-US", "en", None):
        start_url = reverse("pontoon.teams.team", kwargs={"locale": locale})
    else:
        start_url = reverse("pontoon.teams")

    homepage = Homepage.objects.last()

    content = Template(homepage.text).render(Context({"start_url": start_url}))

    return render(
        request,
        "homepage.html",
        {"content": content, "title": homepage.title, "homepage_id": homepage.id},
    )


def _top_contributed_locale(user: User) -> str | None:
    """Locale the user has made the most contributions to."""
    top = (
        Translation.objects.filter(user=user)
        .values("locale__code")
        .annotate(total=Count("locale__code"))
        .distinct()
        .order_by("-total")
        .first()
    )
    return top["locale__code"] if top else None
