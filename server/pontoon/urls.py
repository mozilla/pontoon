from django.conf.urls.defaults import *

urlpatterns = patterns('pontoon.views',
    (r'^$', 'stats'),
    (r'^push/', 'push'),
)
