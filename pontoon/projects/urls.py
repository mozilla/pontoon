from django.conf.urls import url
from django.views.generic import RedirectView

import views

urlpatterns = [
    # Legacy: Redirect to /projects
    url(r'^project/$',
        RedirectView.as_view(url="/projects/", permanent=True)),

    # Legacy: Redirect to /projects/slug
    url(r'^project/(?P<slug>[\w-]+)/$',
        RedirectView.as_view(url="/projects/%(slug)s/", permanent=True)),

    # Active projects
    url(r'^projects/$',
        views.projects,
        name='pontoon.projects'),

    # Project page
    url(r'^projects/(?P<slug>[\w-]+)/$',
        views.project,
        name='pontoon.projects.project'),

    # Project contributors
    url(r'^projects/(?P<slug>[\w-]+)/contributors/$',
        views.project,
        name='pontoon.projects.contributors'),

    # Project info
    url(r'^projects/(?P<slug>[\w-]+)/info/$',
        views.project,
        name='pontoon.projects.info'),

    # AJAX view: Project teams
    url(r'^projects/(?P<slug>[\w-]+)/ajax/$',
        views.ajax_teams,
        name='pontoon.projects.ajax.teams'),

    # AJAX view: Project contributors
    url(r'^projects/(?P<slug>[\w-]+)/ajax/contributors/$',
        views.ProjectContributorsView.as_view(),
        name='pontoon.projects.ajax.contributors'),

    # AJAX view: Project info
    url(r'^projects/(?P<slug>[\w-]+)/ajax/info/$',
        views.ajax_info,
        name='pontoon.projects.ajax.info'),
]
