from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from funfactory.monkeypatches import patch
patch()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Main app:
    (r'', include('pontoon.base.urls')),

    # Admin:
    (r'admin/', include('pontoon.administration.urls')),

    # BrowserID:
    url(r'^browserid/$', 'pontoon.base.views.verify', name='browserid.verify'),

    # Logout
    url(r'^signout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='signout'),

    # 404 and 500
    url(r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
    url(r'^500/$', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),

    # Favicon
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),

    # Django admin
    (r'^a/', include(admin.site.urls)),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
