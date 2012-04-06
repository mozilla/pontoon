from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='pontoon.home'),
    url(r'^bleach/?$', views.bleach_test, name='pontoon.bleach'),
)
