import pontoon.tags.admin.views as tags_admin_views

from . import views
from django.urls import include, path


urlpatterns = [
    # Admin Home
    path("", views.admin, name="pontoon.admin"),
    # AJAX view: Project tags
    path(
        "projects/<slug:project>/ajax/tag/<slug:tag>/",
        tags_admin_views.ProjectTagAdminAjaxView.as_view(),
        name="pontoon.admin.project.ajax.tag",
    ),
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
                # Project strings
                path(
                    "strings/",
                    views.manage_project_strings,
                    name="pontoon.admin.project.strings",
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
    # AJAX view: Get slug
    path("get-slug/", views.get_slug, name="pontoon.admin.project.slug"),
    # AJAX view: Get project locales
    path(
        "get-project-locales/",
        views.get_project_locales,
        name="pontoon.admin.project.locales",
    ),
]
