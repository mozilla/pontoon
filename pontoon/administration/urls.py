from django.conf.urls.defaults import *

import views


urlpatterns = patterns('',
    url(r'^$', views.admin, name='pontoon.admin'),
    url(r'^project/$', views.admin_project, name='pontoon.admin.project.new'),
    url(r'^project/(?P<name>\S+)/$', views.admin_project, name='pontoon.admin.project'),
    url(r'^svn/$', views.update_from_svn, name='pontoon.svn.update'),
    url(r'^transifex/$', views.update_from_transifex, name='pontoon.transifex.update'),
)
