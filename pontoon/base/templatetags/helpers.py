import cgi
import datetime
import json
import urllib
import urlparse

from django.contrib.humanize.templatetags import humanize
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str

import jinja2
from django_jinja import library


@library.global_function
def thisyear():
    """The current year."""
    return jinja2.Markup(datetime.date.today().year)


@library.global_function
def url(viewname, *args, **kwargs):
    """Helper for Django's ``reverse`` in templates."""
    return reverse(viewname, args=args, kwargs=kwargs)


@library.filter
def urlparams(url_, hash=None, **query):
    """Add a fragment and/or query paramaters to a URL.

    New query params will be appended to exising parameters, except duplicate
    names, which will be replaced.
    """
    url = urlparse.urlparse(url_)
    fragment = hash if hash is not None else url.fragment

    # Use dict(parse_qsl) so we don't get lists of values.
    q = url.query
    query_dict = dict(urlparse.parse_qsl(smart_str(q))) if q else {}
    query_dict.update((k, v) for k, v in query.items())

    query_string = _urlencode([(k, v) for k, v in query_dict.items()
                               if v is not None])
    new = urlparse.ParseResult(url.scheme, url.netloc, url.path, url.params,
                               query_string, fragment)
    return new.geturl()


def _urlencode(items):
    """A Unicode-safe URLencoder."""
    try:
        return urllib.urlencode(items)
    except UnicodeEncodeError:
        return urllib.urlencode([(k, smart_str(v)) for k, v in items])


@library.filter
def urlencode(txt):
    """Url encode a path."""
    if isinstance(txt, unicode):
        txt = txt.encode('utf-8')
    return urllib.quote_plus(txt)


@library.global_function
def static(path):
    return staticfiles_storage.url(path)


@library.filter
def to_json(value):
    return json.dumps(value)


@library.filter
def naturalday(source, arg=None):
    return humanize.naturalday(source, arg)


@library.filter
def naturaltime(source):
    return humanize.naturaltime(source)


@library.filter
def display_permissions(self):
    output = 'Can make suggestions'

    if self.translated_locales:
        if self.is_superuser:
            locales = 'all locales'
        else:
            locales = ', '.join(self.translated_locales)
        output = 'Can submit and approve translations for ' + locales

    return output


@library.filter
def format_datetime(value, format='full'):
    if value is not None:
        if format == 'full':
            format = '%A, %B %d, %Y at %H:%M %Z'
        elif format == 'date':
            format = '%B %d, %Y'
        elif format == 'time':
            format = '%H:%M %Z'
        return value.strftime(format)
    else:
        return '---'


@library.filter
def format_timedelta(value):
    if value is not None:
        parts = []
        if value.days > 0:
            parts.append('{0} days'.format(value.days))
        minutes = value.seconds // 60
        seconds = value.seconds % 60
        if minutes > 0:
            parts.append('{0} minutes'.format(minutes))
        if seconds > 0:
            parts.append('{0} seconds'.format(seconds))

        if parts:
            return ', '.join(parts)
        else:
            return '0 seconds'
    else:
        return '---'


@library.filter
def nospam(self):
    return jinja2.Markup(cgi.escape(self, True).replace('@', '&#64;').replace('.', '&#46;').replace('\'', '&quot;'))
