from . import views
from django.urls import path
from django.views.generic import RedirectView


LOCALE_PART = r"(?P<locale>[A-Za-z0-9\-\@\.]+)"
PROJECT_PART = r"(?P<project>[\w-]+)"
RESOURCE_PART = r"(?P<resource>.+)"


urlpatterns = [
    # For backwards compatibility, redirect old `translate/` URLs.
    path(
        "translate/<locale:locale>/<slug:project>/<path:resource>/",
        RedirectView.as_view(
            url="/%(locale)s/%(project)s/%(resource)s/",
            query_string=True,
            permanent=False,
        ),
    ),
    path(
        "<locale:locale>/<slug:project>/<path:resource>/",
        views.translate,
        name="pontoon.translate",
    ),
]
