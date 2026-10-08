from django.urls import include, path

from . import views


urlpatterns = [
    # Admin Home
    path("", views.admin, name="pontoon.admin"),
    # Add new project
    path("projects/", views.manage_project, name="pontoon.admin.project.new"),
    # Project-related views
    path(
        "projects/<slug:slug>/",
        include(
            [
                # Sync project
                path(
                    "sync/",
                    views.manually_sync_project,
                    name="pontoon.admin.project.sync",
                ),
                # Pretranslate project
                path(
                    "pretranslate/",
                    views.manually_pretranslate_project,
                    name="pontoon.admin.project.pretranslate",
                ),
                # Edit project
                path("", views.manage_project, name="pontoon.admin.project"),
            ]
        ),
    ),
    # Calculate Stats
    path(
        "calculate-stats/",
        views.manually_calculate_stats,
        name="pontoon.admin.calculate-stats",
    ),
    # AJAX view: Get slug
    path("get-slug/", views.get_slug, name="pontoon.admin.project.slug"),
    # AJAX view: Get project locales
    path(
        "get-project-locales/",
        views.get_project_locales,
        name="pontoon.admin.project.locales",
    ),
]
