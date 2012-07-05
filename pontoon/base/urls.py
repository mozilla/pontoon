from django.conf.urls.defaults import *

import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='pontoon.home'),
    url(r'^locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/url/(?P<url>\S+)/$', views.home, name='pontoon.translate'),
    url(r'^checkurl/', views.check_url, name='pontoon.checkurl'),
    url(r'^get/', views.get_translation, name='pontoon.get'),
    url(r'^load/', views.load_entities, name='pontoon.get'),
    url(r'^download/', views.download, name='pontoon.download'),
    url(r'^transifex/', views.transifex_save, name='pontoon.transifex'),
)
