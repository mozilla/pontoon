from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='examples.home'),
    url(r'^bleach/?$', views.bleach_test, name='examples.bleach'),
)
