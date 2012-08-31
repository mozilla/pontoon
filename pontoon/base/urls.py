from django.conf.urls.defaults import *

import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='pontoon.home'),
    url(r'^error/$', views.home, name='pontoon.error'),
    url(r'^locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/url/(?P<url>\S+)/$', views.translate, name='pontoon.translate'),
    url(r'^get/', views.get_translation, name='pontoon.get'),
    url(r'^save/', views.save_translation, name='pontoon.save'),
    url(r'^load/', views.load_entities, name='pontoon.load'),
    url(r'^download/', views.download, name='pontoon.download'),
    url(r'^svn/$', views.commit_to_svn, name='pontoon.svn'),
    url(r'^transifex/$', views.save_to_transifex, name='pontoon.transifex'),
    url(r'^csrf/$', views.get_csrf, name='pontoon.csrf'),
)
