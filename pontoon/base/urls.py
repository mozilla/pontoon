from django.urls import path
from django.views.generic import RedirectView, TemplateView

from . import views

urlpatterns = [
    # Terms
    path(
        "terms/",
        TemplateView.as_view(template_name="terms.html"),
        name="pontoon.terms",
    ),
    # TRANSLATE URLs
    # Legacy: Translate project's page
    path(
        "<locale:locale>/project/<slug:slug>/page/<path:page>/",
        RedirectView.as_view(url="/%(locale)s/%(slug)s/%(page)s/", permanent=True),
    ),
    # Legacy: Translate project
    path(
        "locale/<locale:locale>/project/<slug:slug>/",
        RedirectView.as_view(url="/%(locale)s/%(slug)s/", permanent=True),
    ),
    # AJAX: Get locale details
    path(
        "teams/<locale:locale>/projects/",
        views.locale_projects,
        name="pontoon.locale.projects",
    ),
    # AJAX: Get locale stats used in All Resources part
    path(
        "teams/<locale:locale>/stats/", views.locale_stats, name="pontoon.locale.stats",
    ),
    # AJAX: Get locale-project pages/paths with stats
    path(
        "<locale:locale>/<slug:slug>/parts/",
        views.locale_project_parts,
        name="pontoon.locale.project.parts",
    ),
    # AJAX: Get authors and time range data
    path(
        "<locale:locale>/<slug:slug>/<path:part>/authors-and-time-range/",
        views.authors_and_time_range,
        name="pontoon.authors.and.time.range",
    ),
    # Locale-agnostic links
    path(
        "projects/<slug:slug>/<path:part>/",
        views.translate_locale_agnostic,
        name="pontoon.translate.locale.agnostic",
    ),
    # Download translation memory
    path(
        "translation-memory/<locale:locale>.<slug:slug>.tmx",
        views.download_translation_memory,
        name="pontoon.download_tmx",
    ),
    # AJAX
    path("get-entities/", views.entities, name="pontoon.entities"),
    path("get-users/", views.get_users, name="pontoon.get_users"),
    path("perform-checks/", views.perform_checks, name="pontoon.perform.checks"),
    path("get-history/", views.get_translation_history, name="pontoon.get_history"),
    path(
        "get-team-comments/", views.get_team_comments, name="pontoon.get_team_comments",
    ),
    path("add-comment/", views.add_comment, name="pontoon.add_comment",),
    path("pin-comment/", views.pin_comment, name="pontoon.pin_comment",),
    path("unpin-comment/", views.unpin_comment, name="pontoon.unpin_comment",),
    path(
        "other-locales/",
        views.get_translations_from_other_locales,
        name="pontoon.other_locales",
    ),
    path(
        "translations/",
        views.download_translations,
        name="pontoon.download.translations",
    ),
    path("upload/", views.upload, name="pontoon.upload"),
    path("user-data/", views.user_data, name="pontoon.user_data"),
]
