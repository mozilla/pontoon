from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Legacy: Redirect to /projects
    url(r"^project/$", RedirectView.as_view(url="/projects/", permanent=True)),
    # Legacy: Redirect to /projects/slug
    url(
        r"^project/(?P<slug>[\w-]+)/$",
        RedirectView.as_view(url="/projects/%(slug)s/", permanent=True),
    ),
    # Active projects
    url(r"^projects/$", views.projects, name="pontoon.projects"),
    # Project page
    url(
        r"^projects/(?P<slug>[\w-]+)/$", views.project, name="pontoon.projects.project"
    ),
    # Project tags
    url(
        r"^projects/(?P<slug>[\w-]+)/tags/$",
        views.project,
        name="pontoon.projects.tags",
    ),
    # Project contributors
    url(
        r"^projects/(?P<slug>[\w-]+)/contributors/$",
        views.project,
        name="pontoon.projects.contributors",
    ),
    # Project info
    url(
        r"^projects/(?P<slug>[\w-]+)/info/$",
        views.project,
        name="pontoon.projects.info",
    ),
    # Project notifications
    url(
        r"^projects/(?P<slug>[\w-]+)/notifications/$",
        views.project,
        name="pontoon.projects.notifications",
    ),
    # AJAX view: Project teams
    url(
        r"^projects/(?P<slug>[\w-]+)/ajax/$",
        views.ajax_teams,
        name="pontoon.projects.ajax.teams",
    ),
    # AJAX view: Project tags
    url(
        r"^projects/(?P<slug>[\w-]+)/ajax/tags/$",
        views.ajax_tags,
        name="pontoon.projects.ajax.tags",
    ),
    # AJAX view: Project contributors
    url(
        r"^projects/(?P<slug>[\w-]+)/ajax/contributors/$",
        views.ProjectContributorsView.as_view(),
        name="pontoon.projects.ajax.contributors",
    ),
    # AJAX view: Project info
    url(
        r"^projects/(?P<slug>[\w-]+)/ajax/info/$",
        views.ajax_info,
        name="pontoon.projects.ajax.info",
    ),
    # AJAX view: Project notifications
    url(
        r"^projects/(?P<slug>[\w-]+)/ajax/notifications/$",
        views.ajax_notifications,
        name="pontoon.projects.ajax.notifications",
    ),
]
