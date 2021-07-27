from django.urls import include, path, register_converter
from django.urls.converters import StringConverter
from django.contrib import admin
from django.contrib.auth import logout
from django.views.generic import RedirectView, TemplateView

from pontoon.teams.views import team


class LocaleConverter(StringConverter):
    regex = r"[A-Za-z0-9\-\@\.]+"


register_converter(LocaleConverter, "locale")

pontoon_js_view = TemplateView.as_view(
    template_name="js/pontoon.js", content_type="text/javascript"
)

permission_denied_view = TemplateView.as_view(template_name="403.html")
page_not_found_view = TemplateView.as_view(template_name="404.html")
server_error_view = TemplateView.as_view(template_name="500.html")

urlpatterns = [
    # Legacy: Locale redirect for compatibility with i18n ready URL scheme
    path("en-US<path:url>", RedirectView.as_view(url="%(url)s", permanent=True)),
    # Redirect legacy Aurora projects
    path(
        "projects/firefox-aurora/<path:url>",
        RedirectView.as_view(url="/projects/firefox/%(url)s", permanent=True),
    ),
    path(
        "projects/firefox-for-android-aurora/<path:url>",
        RedirectView.as_view(
            url="/projects/firefox-for-android/%(url)s", permanent=True
        ),
    ),
    path(
        "projects/thunderbird-aurora/<path:url>",
        RedirectView.as_view(url="/projects/thunderbird/%(url)s", permanent=True),
    ),
    path(
        "projects/lightning-aurora/<path:url>",
        RedirectView.as_view(url="/projects/lightning/%(url)s", permanent=True),
    ),
    path(
        "projects/seamonkey-aurora/<path:url>",
        RedirectView.as_view(url="/projects/seamonkey/%(url)s", permanent=True),
    ),
    path(
        "<locale:locale>/firefox-aurora/<path:url>",
        RedirectView.as_view(url="/%(locale)s/firefox/%(url)s", permanent=True),
    ),
    path(
        "<locale:locale>/firefox-for-android-aurora/<path:url>",
        RedirectView.as_view(
            url="/%(locale)s/firefox-for-android/%(url)s", permanent=True
        ),
    ),
    path(
        "<locale:locale>/thunderbird-aurora/<path:url>",
        RedirectView.as_view(url="/%(locale)s/thunderbird/%(url)s", permanent=True),
    ),
    path(
        "<locale:locale>/lightning-aurora/<path:url>",
        RedirectView.as_view(url="/%(locale)s/lightning/%(url)s", permanent=True),
    ),
    path(
        "<locale:locale>/seamonkey-aurora/<path:url>",
        RedirectView.as_view(url="/%(locale)s/seamonkey/%(url)s", permanent=True),
    ),
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
    # Include script
    path("pontoon.js", pontoon_js_view),
    path("static/js/pontoon.js", pontoon_js_view),
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
    path("", include("pontoon.in_context.urls")),
    path("", include("pontoon.uxactionlog.urls")),
    # Team page: Must be at the end
    path("<locale:locale>/", team, name="pontoon.teams.team"),
]
