from django.conf.urls import patterns, url

from pontoon.translate import views


urlpatterns = patterns(
    '',

    # Main translation page
    url(r'^project/(?P<project_slug>[\w-]+)/locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/translate/$',
        views.index, name='pontoon.translate.index'),


    url(r'^project/(?P<project_slug>[\w-]+)/locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/entities$',
        views.entities, name='pontoon.translate.entities'),
)
