from django.conf.urls import url

import views


urlpatterns = [
    # Admin Home
    url(r'^$', views.admin,
        name='pontoon.admin'),

    # Add new project
    url(r'^projects/$', views.manage_project,
        name='pontoon.admin.project.new'),

    # Edit project
    url(r'^projects/(?P<slug>.+)/$', views.manage_project,
        name='pontoon.admin.project'),

    # Get slug
    url(r'^get-slug/$', views.get_slug,
        name='pontoon.admin.get_slug'),
]
