from django.conf.urls.defaults import *


urlpatterns = patterns('examples.views',
    url(r'^$', 'home', name='examples.home'),
    url(r'^bleach/?$', 'bleach_test', name='examples.bleach'),
)
