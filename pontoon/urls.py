from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.generic import TemplateView


urlpatterns = patterns('',
    # Legacy: Locale redirect for compatibility with i18n ready URL scheme
    (r'^en-US(?P<url>.+)$', RedirectView.as_view(url="%(url)s", permanent=True)),

    # Admin
    (r'admin/', include('pontoon.administration.urls')),

    # Django admin
    (r'^a/', include(admin.site.urls)),

    # Test project: Pontoon Intro
    url(r'^intro/$', 'pontoon.intro.views.intro'),

    # BrowserID
    (r'', include('django_browserid.urls')),

    # Logout
    url(r'^signout/$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='signout'),

    # Error pages
    url(r'^403/$', TemplateView.as_view(template_name='403.html')),
    url(r'^404/$', TemplateView.as_view(template_name='404.html')),
    url(r'^500/$', TemplateView.as_view(template_name='500.html')),

    # Favicon
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),

    # Include script
    url(r'^pontoon\.js$',
        RedirectView.as_view(url='/static/js/pontoon.js', permanent=True)),

    # Main app: Must be at the end
    (r'', include('pontoon.translate.urls')),

    # Main app: Must be at the end
    (r'', include('pontoon.base.urls')),
)
