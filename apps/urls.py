from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .examples import urls

from funfactory.monkeypatches import patch
patch()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Main app:
    (r'', include('apps.pontoon.urls')),

    # BrowserID:
    url(r'^browserid/verify/$', 'apps.pontoon.views.verify', name='browserid.verify'),

    # Logout
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
