from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout
from django.views.generic import RedirectView, TemplateView
from pontoon.base.views import heroku_setup
from pontoon.intro.views import intro
from pontoon.teams.views import team

pontoon_js_view = TemplateView.as_view(template_name='js/pontoon.js', content_type='text/javascript')

urlpatterns = [
    # Legacy: Locale redirect for compatibility with i18n ready URL scheme
    url(r'^en-US(?P<url>.+)$', RedirectView.as_view(url="%(url)s", permanent=True)),

    # Redirect similar locales
    url(r'^ga/(?P<url>.*)$', RedirectView.as_view(url="/ga-IE/%(url)s", permanent=True)),
    url(r'^pt/(?P<url>.*)$', RedirectView.as_view(url="/pt-PT/%(url)s", permanent=True)),

    # Accounts
    url(r'^accounts/', include('pontoon.allauth_urls')),

    # Admin
    url(r'^admin/', include('pontoon.administration.urls')),

    # Django admin
    url(r'^a/', include(admin.site.urls)),

    # Test project: Pontoon Intro
    url(r'^intro/$', intro),

    # Logout
    url(r'^signout/$', logout, {'next_page': '/'}, name='signout'),

    # Error pages
    url(r'^403/$', TemplateView.as_view(template_name='403.html')),
    url(r'^404/$', TemplateView.as_view(template_name='404.html')),
    url(r'^500/$', TemplateView.as_view(template_name='500.html')),

    # Urls related to integration with Heroku
    url(r'^heroku-setup/', heroku_setup,
        name='pontoon.heroku_setup'),

    # Robots.txt
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    # contribute.json
    url(r'^contribute.json$', TemplateView.as_view(template_name='contribute.json', content_type='text/plain')),

    # Favicon
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),

    # Include script
    url(r'^pontoon\.js$', pontoon_js_view),
    url(r'^static/js/pontoon\.js$', pontoon_js_view),

    # Include URL configurations from installed apps
    url(r'', include('pontoon.teams.urls')),
    url(r'', include('pontoon.sync.urls')),
    url(r'', include('pontoon.projects.urls')),
    url(r'', include('pontoon.machinery.urls')),
    url(r'', include('pontoon.contributors.urls')),
    url(r'', include('pontoon.localizations.urls')),
    url(r'', include('pontoon.base.urls')),

    # Team page: Must be at the end
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/$', team, name='pontoon.teams.team'),
]
