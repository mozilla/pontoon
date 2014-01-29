from django.conf.urls.defaults import *

import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='pontoon.home'),
    url('^translate/error/$', views.handle_error, name='pontoon.handle_error'),
    url(r'^locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/site/(?P<url>.+)/$',
        views.translate_site,
        name='pontoon.translate.site'),
    url(r'^locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/project/(?P<project>.+)/page/(?P<page>.+)/$',
        views.translate_project,
        name='pontoon.translate.project.page'),
    url(r'^locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/project/(?P<project>.+)/$',
        views.translate_project,
        name='pontoon.translate.project'),

    url(r'^get/', views.get_translation, name='pontoon.get'),
    url(r'^update/', views.update_translation, name='pontoon.update'),
    url(r'^mt/$', views.machine_translation, name='pontoon.mt'),
    url(r'^download/', views.download, name='pontoon.download'),
    url(r'^svn/$', views.commit_to_svn, name='pontoon.svn'),
    url(r'^transifex/$', views.save_to_transifex, name='pontoon.transifex'),
    url(r'^csrf/$', views.get_csrf, name='pontoon.csrf'),
)
