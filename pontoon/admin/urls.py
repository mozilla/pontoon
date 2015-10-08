from django.conf.urls import include, patterns, url

from pontoon.admin import views
from pontoon.admin.site import admin_site


urlpatterns = patterns(
    '',

    # Custom views
    url(r'^base/project/(?P<pk>\d+)/sync/$', views.project_trigger_sync,
        name='pontoon.admin.project_trigger_sync'),

    # Main Admin Views
    url(r'', include(admin_site.urls)),
)
