import html
import datetime
import json

import markupsafe
from allauth.socialaccount import providers
from allauth.utils import get_request_param
from bleach.linkifier import Linker
from django_jinja import library

from django import template
from django.conf import settings
from django.contrib.humanize.templatetags import humanize
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from pontoon.base.fluent import get_simple_preview

register = template.Library()


@library.global_function
def url(viewname, *args, **kwargs):
    """Helper for Django's ``reverse`` in templates."""
    return reverse(viewname, args=args, kwargs=kwargs)


@library.global_function
def return_url(request):
    """Get an url of the previous page."""
    url = request.POST.get("return_url", request.META.get("HTTP_REFERER", "/"))
    if not url_has_allowed_host_and_scheme(url, settings.ALLOWED_HOSTS):
        return settings.SITE_URL
    return url


@library.global_function
def static(path):
    return staticfiles_storage.url(path)


@library.filter
def to_json(value):
    return json.dumps(value, cls=DjangoJSONEncoder)


@library.filter
def naturaltime(source):
    return humanize.naturaltime(source)


@library.filter
def intcomma(source):
    return humanize.intcomma(source)


@library.filter
def metric_prefix(source):
    """
    Format numbers with metric prefixes.

    Inspired by: https://stackoverflow.com/a/9462382
    """
    prefixes = [
        {"value": 1e18, "symbol": "E"},
        {"value": 1e15, "symbol": "P"},
        {"value": 1e12, "symbol": "T"},
        {"value": 1e9, "symbol": "G"},
        {"value": 1e6, "symbol": "M"},
        {"value": 1e3, "symbol": "k"},
        {"value": 1, "symbol": ""},
    ]

    for prefix in prefixes:
        if source >= prefix["value"]:
            break

    # Divide source number by the first lower prefix value
    output = source / prefix["value"]

    # Round quotient to 1 decimal point
    output = f"{output:.1f}"

    # Remove decimal point if 0
    output = output.rstrip("0").rstrip(".")

    # Append prefix symbol
    output += prefix["symbol"]

    return output


@library.filter
def comma_or_prefix(source):
    if source >= 100000:
        return metric_prefix(source)
    return humanize.intcomma(source)


@library.filter
def date_status(value, complete):
    """Get date status relative to today."""
    if isinstance(value, datetime.date):
        if not complete:
            today = datetime.date.today()
            if value <= today:
                return "overdue"
            elif (value - today).days < 8:
                return "approaching"
    else:
        return "not"

    return "normal"


@library.filter
def format_datetime(value, format="full", default="---"):
    if value is not None:
        if format == "full":
            format = "%A, %B %d, %Y at %H:%M %Z"
        elif format == "date":
            format = "%B %-d, %Y"
        elif format == "short_date":
            format = "%b %-d, %Y"
        elif format == "time":
            format = "%H:%M %Z"
        return value.strftime(format)
    else:
        return default


@library.filter
def format_timedelta(value):
    if value is not None:
        parts = []
        if value.days > 0:
            parts.append(f"{value.days} days")
        minutes = value.seconds // 60
        seconds = value.seconds % 60
        if minutes > 0:
            parts.append(f"{minutes} minutes")
        if seconds > 0:
            parts.append(f"{seconds} seconds")

        if parts:
            return ", ".join(parts)
        else:
            return "0 seconds"
    else:
        return "---"


@register.filter
@library.filter
def nospam(self):
    return markupsafe.Markup(
        html.escape(self, True).replace("@", "&#64;").replace(".", "&#46;")
    )


@library.global_function
def provider_login_url(request, provider_id=settings.AUTHENTICATION_METHOD, **query):
    """
    This function adapts the django-allauth templatetags that don't support jinja2.
    @TODO: land support for the jinja2 tags in the django-allauth.
    """
    provider = providers.registry.by_id(provider_id)

    auth_params = query.get("auth_params", None)
    process = query.get("process", None)

    if auth_params == "":
        del query["auth_params"]

    if "next" not in query:
        next_ = get_request_param(request, "next")
        if next_:
            query["next"] = next_
        elif process == "redirect":
            query["next"] = request.get_full_path()
    else:
        if not query["next"]:
            del query["next"]
    return provider.get_login_url(request, **query)


@library.global_function
def providers_media_js(request):
    """A port of django tag into jinja2"""
    return markupsafe.Markup(
        "\n".join([p.media_js(request) for p in providers.registry.get_list()])
    )


@library.filter
def pretty_url(url):
    """Remove protocol and www"""
    url = url.split("://")[1]
    if url.startswith("www."):
        url = url[4:]

    return url


@library.filter
def local_url(url, code=None):
    """Replace occurences of `{locale_code} in URL with provided code."""
    code = code or "en-US"
    return url.format(locale_code=code)


@library.filter
def dict_html_attrs(dict_obj):
    """Render json object properties into a series of data-* attributes."""
    return markupsafe.Markup(" ".join([f'data-{k}="{v}"' for k, v in dict_obj.items()]))


@library.filter
def as_plain_message(source):
    """
    Return a plain string representation of a given message.

    Complex FTL strings are transformed into single-value strings.
    """
    return get_simple_preview(source)


@library.filter
def linkify(source):
    """Render URLs in the string as links."""

    def set_attrs(attrs, new=False):
        attrs[(None, "target")] = "_blank"
        attrs[(None, "rel")] = "noopener noreferrer"
        return attrs

    # Escape all tags
    linker = Linker(callbacks=[set_attrs])

    return linker.linkify(source)
