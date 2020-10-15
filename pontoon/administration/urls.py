from django.conf.urls import url

from . import views

import pontoon.tags.admin.views as tags_admin_views


urlpatterns = [
    # Admin Home
    url(r"^$", views.admin, name="pontoon.admin"),
    # AJAX view: Project tags
    url(
        r"^projects/(?P<project>[\w-]+)/ajax/tag/(?P<tag>[\w-]+)/$",
        tags_admin_views.ProjectTagAdminAjaxView.as_view(),
        name="pontoon.admin.project.ajax.tag",
    ),
    # Add new project
    url(r"^projects/$", views.manage_project, name="pontoon.admin.project.new"),
    # Sync project
    url(
        r"^projects/(?P<slug>[\w-]+)/sync/$",
        views.manually_sync_project,
        name="pontoon.project.sync",
    ),
    # Sync project
    url(
        r"^projects/(?P<slug>[\w-]+)/strings/$",
        views.manage_project_strings,
        name="pontoon.admin.project.strings",
    ),
    # Pretranslate project
    url(
        r"^projects/(?P<slug>[\w-]+)/pretranslate/$",
        views.manually_pretranslate_project,
        name="pontoon.project.sync",
    ),
    # Edit project
    url(
        r"^projects/(?P<slug>.+)/$", views.manage_project, name="pontoon.admin.project"
    ),
    # Get slug
    url(r"^get-slug/$", views.get_slug, name="pontoon.admin.get_slug"),
]
