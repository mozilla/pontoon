from django.urls import include, path, re_path

from pontoon.projects import views as projects_views
from pontoon.teams import views as teams_views

from . import views

urlpatterns = [
    path(
        "<locale:code>/<slug:slug>/",
        include(
            [
                # Localization page
                path(
                    "", views.localization, name="pontoon.localizations.localization",
                ),
                # Localization tags
                path("tags/", views.localization, name="pontoon.localizations.tags",),
                # Localization contributors
                path(
                    "contributors/",
                    views.localization,
                    name="pontoon.localizations.contributors",
                ),
                # Project info
                path(
                    "project-info/",
                    views.localization,
                    name="pontoon.localizations.project-info",
                ),
                # Team info
                path(
                    "team-info/",
                    views.localization,
                    name="pontoon.localizations.team-info",
                ),
                # AJAX views
                path(
                    "ajax/",
                    include(
                        [
                            # Localization resources
                            path(
                                "",
                                views.ajax_resources,
                                name="pontoon.localizations.ajax.resources",
                            ),
                            # Localization tags
                            path(
                                "tags/",
                                views.ajax_tags,
                                name="pontoon.localizations.ajax.tags",
                            ),
                            # Localization contributors
                            path(
                                "contributors/",
                                views.LocalizationContributorsView.as_view(),
                                name="pontoon.localizations.ajax.contributors",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
    # AJAX view: Project info
    re_path(
        r"^[A-Za-z0-9\-\@\.]+/(?P<slug>[\w-]+)/ajax/project-info/$",
        projects_views.ajax_info,
        name="pontoon.localizations.ajax.project-info",
    ),
    # AJAX view: Team info
    re_path(
        r"^(?P<locale>[A-Za-z0-9\-\@\.]+)/[\w-]+/ajax/team-info/$",
        teams_views.ajax_info,
        name="pontoon.localizations.ajax.team-info",
    ),
]
