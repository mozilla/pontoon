from django.conf.urls import url

from . import views


urlpatterns = [
    # Project tag page
    url(
        r"^projects/(?P<project>[\w-]+)/tags/(?P<tag>[\w-]+)/$",
        views.ProjectTagView.as_view(),
        name="pontoon.tags.project.tag",
    ),
    # AJAX view: Project tag teams
    url(
        r"^projects/(?P<project>[\w-]+)/ajax/tags/(?P<tag>[\w-]+)/$",
        views.ProjectTagView.as_view(),
        name="pontoon.tags.ajax.teams",
    ),
]
