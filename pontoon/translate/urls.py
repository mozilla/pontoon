from django.conf.urls import patterns, url

from pontoon.translate import views


urlpatterns = patterns(
    '',

    # Main translation page
    url(r'^projects/(?P<project_slug>[\w-]+)/locales/(?P<locale>[A-Za-z0-9\-\@\.]+)/translate/$',
        views.index, name='pontoon.translate.index'),

    url(r'^projects/$', views.projects, name='pontoon.translate.projects'),

    url(r'^projects/(?P<project_slug>[\w-]+)/locales/(?P<locale>[A-Za-z0-9\-\@\.]+)/entities/$',
        views.entities, name='pontoon.translate.entities'),

    url(r'^entities/(?P<entity_pk>[0-9]+)/translations/(?P<locale_code>[A-Za-z0-9\-\@\.]+)/$',
        views.translations, name='pontoon.translate.entities.translations'),
)
