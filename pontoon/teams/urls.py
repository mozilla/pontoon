from django.urls import include, path
from django.views.generic import RedirectView

from . import views


urlpatterns = [
    # Localization teams
    path("teams/", views.teams, name="pontoon.teams"),
    # AJAX: Request team to be added to Pontoon
    path("teams/request/", views.request_item, name="pontoon.teams.request.locale"),
    # Redirect to a team page
    path(
        "teams/<locale:locale>/",
        RedirectView.as_view(url="/%(locale)s/", permanent=True),
    ),
    path(
        "<locale:locale>/",
        include(
            [
                # Team contributors
                path("contributors/", views.team, name="pontoon.teams.contributors",),
                # Team insights
                path("insights/", views.team, name="pontoon.teams.insights",),
                # Team bugs
                path("bugs/", views.team, name="pontoon.teams.bugs",),
                # Team info
                path("info/", views.team, name="pontoon.teams.info",),
                # Team permissions
                path("permissions/", views.team, name="pontoon.teams.permissions",),
                # Legacy url for permissions management
                path(
                    "manage/",
                    RedirectView.as_view(
                        url="/%(locale)s/permissions/", permanent=True
                    ),
                    name="pontoon.teams.manage",
                ),
                # AJAX views
                path(
                    "ajax/",
                    include(
                        [
                            # Team projects
                            path(
                                "",
                                views.ajax_projects,
                                name="pontoon.teams.ajax.projects",
                            ),
                            # Team contributors
                            path(
                                "contributors/",
                                views.LocaleContributorsView.as_view(),
                                name="pontoon.teams.ajax.contributors",
                            ),
                            # Team insights
                            path(
                                "insights/",
                                views.ajax_insights,
                                name="pontoon.teams.ajax.insights",
                            ),
                            # Team info
                            path(
                                "info/",
                                views.ajax_info,
                                name="pontoon.teams.ajax.info",
                            ),
                            # Update team info
                            path(
                                "update-info/",
                                views.ajax_update_info,
                                name="pontoon.teams.ajax.update-info",
                            ),
                            # Team permissions
                            path(
                                "permissions/",
                                views.ajax_permissions,
                                name="pontoon.teams.ajax.permissions",
                            ),
                        ]
                    ),
                ),
                # AJAX: Request projects to be added to locale
                path(
                    "request/",
                    views.request_item,
                    name="pontoon.teams.request.projects",
                ),
            ]
        ),
    ),
]
