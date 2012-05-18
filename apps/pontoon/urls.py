from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='pontoon.home'),
    url(r'^locale/(?P<locale>[A-Za-z\-]+)/url/(?P<url>\S+)/$', views.home, name='pontoon.translate'),
    url(r'^checkurl/', views.check_url, name='pontoon.checkurl'),
    url(r'^download/', views.download, name='pontoon.download'),
    url(r'^transifex/', views.transifex, name='pontoon.transifex'),
)
