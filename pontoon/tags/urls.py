from django.urls import path

from . import views


urlpatterns = [
    # Project tag page
    path(
        "projects/<slug:project>/tags/<slug:tag>/",
        views.ProjectTagView.as_view(),
        name="pontoon.tags.project.tag",
    ),
    # AJAX view: Project tag teams
    path(
        "projects/<slug:project>/ajax/tags/<slug:tag>/",
        views.ProjectTagView.as_view(),
        name="pontoon.tags.ajax.teams",
    ),
]
