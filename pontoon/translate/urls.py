from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import url

from . import URL_BASE, views


LOCALE_PART = r'(?P<locale>[A-Za-z0-9\-\@\.]+)'
PROJECT_PART = r'(?P<project>[\w-]+)'
RESOURCE_PART = r'(?P<resource>.+)'


urlpatterns = [
    url(
        r'^%s$' % URL_BASE,
        views.translate,
        name='pontoon.translate.next',
    ),
    url(
        r'^{base}{locale}/{project}/{resource}/$'.format(
            base=URL_BASE,
            locale=LOCALE_PART,
            project=PROJECT_PART,
            resource=RESOURCE_PART,
        ),
        views.translate,
        name='pontoon.translate.next',
    ),
]


# For local development, we want to serve front-end static files from the
# webserver that create-react-app is running. This way we benefit from
# hot reloading and all the niceties of React dev tools.
# To do that, we must overwrite the staticfiles serve view, and we also
# want to catch websocket connexions.
#
# Note that because we override the static files serving, you will need to
# run your local django server with the `--nostatic` option. That's
# automatically done when running with `make run`.
if settings.DEV:
    urlpatterns += [
        url(
            r'^static/(?P<path>.*)$',
            views.static_serve_dev,
        ),
        url(
            r'^sockjs-node/.*$',
            views.translate,
        ),
    ]
