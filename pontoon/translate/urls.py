from django.conf import settings
from django.urls import path, re_path
from django.views.generic import RedirectView

from . import views


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


# For local development, we want to serve front-end static files from the
# webserver that create-react-app is running. This way we benefit from
# hot reloading and all the niceties of React dev tools.
# To do that, we must overwrite the staticfiles serve view, and we also
# want to catch websocket connexions.
#
# Note that because we override the static files serving, you will need to
# run your local django server with the `--nostatic` option. That's
# automatically done when running with `make run`.
if settings.DEV:
    urlpatterns += [
        path("static/<path:path>", views.static_serve_dev,),
        re_path(r"^sockjs-node/.*$", views.translate,),
    ]
