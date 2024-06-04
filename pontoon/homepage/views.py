from django.http import Http404
from django.shortcuts import redirect, render
from django.template import Context, Template
from django.urls import reverse
from pontoon.base.models import Locale
from pontoon.base.utils import get_locale_or_redirect, get_project_locale_from_request
from pontoon.homepage.models import Homepage


def homepage(request):
    user = request.user

    # Redirect user to the selected home page or '/'.
    if user.is_authenticated and user.profile.custom_homepage != "":
        # If custom homepage not set yet, set it to the most contributed locale team page
        if user.profile.custom_homepage is None:
            if user.top_contributed_locale:
                user.profile.custom_homepage = user.top_contributed_locale
                user.profile.save(update_fields=["custom_homepage"])

        if user.profile.custom_homepage:
            try:
                # Call to get_locale_or_redirect to check if the custom homepage locale exists
                get_locale_or_redirect(user.profile.custom_homepage)
                return redirect(
                    "pontoon.teams.team", locale=user.profile.custom_homepage
                )
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
