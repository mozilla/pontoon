from django.conf.urls.defaults import *

urlpatterns = patterns('apps.pontoon.views',
    (r'^$', 'stats'),
    (r'^push/', 'push'),
)
