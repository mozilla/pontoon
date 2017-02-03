from django.conf.urls import url

import views


urlpatterns = [
    # Admin Home
    url(r'^$', views.admin,
        name='pontoon.admin'),

    # Add new project
    url(r'^projects/$', views.manage_project,
        name='pontoon.admin.project.new'),

    # Sync project
    url(r'^projects/(?P<slug>[\w-]+)/sync/$',
        views.manually_sync_project,
        name='pontoon.project.sync'),

    # Edit project
    url(r'^projects/(?P<slug>.+)/$', views.manage_project,
        name='pontoon.admin.project'),

    # Get slug
    url(r'^get-slug/$', views.get_slug,
        name='pontoon.admin.get_slug'),
]
