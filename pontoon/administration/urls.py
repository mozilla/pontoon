from django.conf.urls.defaults import *

import views


urlpatterns = patterns('',
    url(r'^a/$', views.admin, name='pontoon.admin'),
    url(r'^a/url/$', views.admin_project, name='pontoon.admin.project.new'),
    url(r'^a/url/(?P<url>\S+)/$', views.admin_project, name='pontoon.admin.project'),
    url(r'^svn/update/$', views.update_from_svn, name='pontoon.svn.update'),
    url(r'^transifex/update/$', views.update_from_transifex, name='pontoon.transifex.update'),
)
