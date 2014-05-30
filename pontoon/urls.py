from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from funfactory.monkeypatches import patch
patch()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',

    # Legacy: Locale redirect for compatibility with i18n ready URL scheme
    (r'^en-US(?P<url>.+)$', RedirectView.as_view(url="%(url)s")),

    # Admin
    (r'admin/', include('pontoon.administration.urls')),

    # Django admin
    (r'^a/', include(admin.site.urls)),

    # BrowserID
    url(r'^browserid/$', 'pontoon.base.views.verify', name='browserid.verify'),

    # Logout
    url(r'^signout/$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='signout'),

    # Error pages
    url(r'^403/$', TemplateView.as_view(template_name='403.html')),
    url(r'^404/$', TemplateView.as_view(template_name='404.html')),
    url(r'^500/$', TemplateView.as_view(template_name='500.html')),

    # Favicon
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/img/favicon.ico')),

    # Include script
    url(r'^pontoon\.js$',
        RedirectView.as_view(url='/static/js/pontoon.js')),

    # Main app: Must be at the end
    (r'', include('pontoon.base.urls')),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
