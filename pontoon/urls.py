from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.generic import TemplateView


urlpatterns = patterns('',
    # Legacy: Locale redirect for compatibility with i18n ready URL scheme
    (r'^en-US(?P<url>.+)$', RedirectView.as_view(url="%(url)s", permanent=True)),

    # Redirect similar locales
    (r'^ga/(?P<url>.*)$', RedirectView.as_view(url="/ga-IE/%(url)s", permanent=True)),
    (r'^pt/(?P<url>.*)$', RedirectView.as_view(url="/pt-PT/%(url)s", permanent=True)),

    # Admin
    (r'admin/', include('pontoon.admin.urls')),

    # Sites
    (r'sites/', include('pontoon.sites.urls')),

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

    # Robots.txt
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    # Robots.txt
    url(r'^contribute.json$', TemplateView.as_view(template_name='contribute.json', content_type='text/plain')),

    # Favicon
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),

    # Include script
    url(r'^pontoon\.js$',
        RedirectView.as_view(url='/static/js/pontoon.js', permanent=True)),

    # Main app: Must be at the end
    (r'', include('pontoon.base.urls')),
)
