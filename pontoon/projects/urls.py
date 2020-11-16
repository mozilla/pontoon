from django.urls import include, path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Legacy: Redirect to /projects
    path("project/", RedirectView.as_view(url="/projects/", permanent=True)),
    # Legacy: Redirect to /projects/slug
    path(
        "project/<slug:slug>/",
        RedirectView.as_view(url="/projects/%(slug)s/", permanent=True),
    ),
    # Active projects
    path("projects/", views.projects, name="pontoon.projects"),
    # Project-related views
    path(
        "projects/<slug:slug>/",
        include(
            [
                # Project page
                path("", views.project, name="pontoon.projects.project"),
                # Project tags
                path("tags/", views.project, name="pontoon.projects.tags",),
                # Project contributors
                path(
                    "contributors/",
                    views.project,
                    name="pontoon.projects.contributors",
                ),
                # Project info
                path("info/", views.project, name="pontoon.projects.info",),
                # Project notifications
                path(
                    "notifications/",
                    views.project,
                    name="pontoon.projects.notifications",
                ),
                # AJAX views
                path(
                    "ajax/",
                    include(
                        [
                            # Project teams
                            path(
                                "",
                                views.ajax_teams,
                                name="pontoon.projects.ajax.teams",
                            ),
                            # Project tags
                            path(
                                r"tags/",
                                views.ajax_tags,
                                name="pontoon.projects.ajax.tags",
                            ),
                            # Project contributors
                            path(
                                "contributors/",
                                views.ProjectContributorsView.as_view(),
                                name="pontoon.projects.ajax.contributors",
                            ),
                            # Project info
                            path(
                                "info/",
                                views.ajax_info,
                                name="pontoon.projects.ajax.info",
                            ),
                            # Project notifications
                            path(
                                "notifications/",
                                views.ajax_notifications,
                                name="pontoon.projects.ajax.notifications",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
