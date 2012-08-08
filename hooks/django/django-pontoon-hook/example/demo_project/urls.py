from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^$', 'demo.views.home', name="home")
)
urlpatterns += staticfiles_urlpatterns()
