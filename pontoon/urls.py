from django.urls import include, path, register_converter
from django.urls.converters import StringConverter
from django.contrib import admin
from django.contrib.auth import logout
from django.views.generic import RedirectView, TemplateView

from pontoon.teams.views import team


class LocaleConverter(StringConverter):
    regex = r"[A-Za-z0-9\-\@\.]+"


register_converter(LocaleConverter, "locale")

permission_denied_view = TemplateView.as_view(template_name="403.html")
page_not_found_view = TemplateView.as_view(template_name="404.html")
server_error_view = TemplateView.as_view(template_name="500.html")

urlpatterns = [
    # Accounts
    path("accounts/", include("pontoon.allauth_urls")),
    # Admin
    path("admin/", include("pontoon.administration.urls")),
    # Django admin: Disable the login form
    path("a/login/", permission_denied_view),
    # Django admin
    path("a/", admin.site.urls),
    # Logout
    path("signout/", logout, {"next_page": "/"}, name="signout"),
    # Error pages
    path("403/", permission_denied_view),
    path("404/", page_not_found_view),
    path("500/", server_error_view),
    # Robots.txt
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    # contribute.json
    path(
        "contribute.json",
        TemplateView.as_view(
            template_name="contribute.json", content_type="text/plain"
        ),
    ),
    # Favicon
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/img/favicon.ico", permanent=True),
    ),
    # Legacy
    path("in-context/", RedirectView.as_view(url="/", permanent=True)),
    path("intro/", RedirectView.as_view(url="/", permanent=True)),
    # Include URL configurations from installed apps
    path("terminology/", include("pontoon.terminology.urls")),
    path("translations/", include("pontoon.translations.urls")),
    path("", include("pontoon.teams.urls")),
    path("", include("pontoon.tour.urls")),
    path("", include("pontoon.tags.urls")),
    path("", include("pontoon.sync.urls")),
    path("", include("pontoon.projects.urls")),
    path("", include("pontoon.machinery.urls")),
    path("", include("pontoon.contributors.urls")),
    path("", include("pontoon.localizations.urls")),
    path("", include("pontoon.base.urls")),
    path("", include("pontoon.translate.urls")),
    path("", include("pontoon.batch.urls")),
    path("", include("pontoon.api.urls")),
    path("", include("pontoon.homepage.urls")),
    path("", include("pontoon.uxactionlog.urls")),
    # Team page: Must be at the end
    path("<locale:locale>/", team, name="pontoon.teams.team"),
]
