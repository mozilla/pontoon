import html
import datetime
import json
import re

import markupsafe
from allauth.socialaccount import providers
from allauth.utils import get_request_param
from bleach.linkifier import Linker
from django_jinja import library
from fluent.syntax import FluentParser, ast, visitor
from fluent.syntax.serializer import serialize_expression

from django import template
from django.conf import settings
from django.contrib.humanize.templatetags import humanize
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


register = template.Library()
parser = FluentParser()


class FlatTransformer(visitor.Transformer):
    """
    - Select expressions are lifted up to the highest possible level,
    duplicating shared contents as necessary.
    - All other Placeables are serialised as TextElements
    - Empty String Literals `{ "" }` are parsed as empty TextElements
    """

    def visit_Attribute(self, node):
        flatten_pattern_elements(node.value)
        return self.generic_visit(node)

    def visit_Message(self, node):
        if node.value:
            flatten_pattern_elements(node.value)
        return self.generic_visit(node)

    def visit_TextElement(self, node):
        node.value = re.sub(r'{ "" }', "", node.value)
        return node


def flatten_pattern_elements(pattern):
    """
    Flattens the given Pattern, uplifting selectors to the highest possible level and
    duplicating shared parts in the variants. All other Placeables are serialised as
    TextElements.

    Should only be called externally with the value of a Message or an Attribute.
    """
    flat_elements = []
    text_fragment = ""
    prev_select = None

    for element in pattern.elements:
        if isinstance(element, ast.Placeable) and isinstance(
            element.expression, ast.SelectExpression
        ):
            # In a message with multiple SelectExpressions separated by some
            # whitespace, keep that whitespace out of select variants.
            if re.search("^\\s+$", text_fragment):
                flat_elements.append(ast.TextElement(text_fragment))
                text_fragment = ""

            # Flatten SelectExpression variant elements
            for variant in element.expression.variants:
                flatten_pattern_elements(variant.value)

                # If there is preceding text, include that for all variants
                if text_fragment:
                    elements = variant.value.elements
                    if elements and isinstance(elements[0], ast.TextElement):
                        first = elements[0]
                        first.value = text_fragment + first.value
                    else:
                        elements.insert(0, ast.TextElement(text_fragment))

            if text_fragment:
                text_fragment = ""

            flat_elements.append(element)
            prev_select = element.expression

        else:
            str_value = (
                element.value
                if isinstance(element, ast.TextElement)
                else serialize_expression(element)
            )
            if text_fragment:
                str_value = text_fragment + str_value
                text_fragment = ""

            if prev_select:
                # Keep trailing whitespace out of variant values
                ws_end = re.match("\\s+$", str_value)
                if ws_end:
                    str_value = str_value[0 : ws_end.index]
                    text_fragment = ws_end[0]

                # If there is a preceding SelectExpression, append to each of its variants
                for variant in prev_select.variants:
                    elements = variant.value.elements
                    if elements and isinstance(elements[-1], ast.TextElement):
                        last = elements[-1]
                        last.value += str_value
                    else:
                        elements.append(ast.TextElement(str_value))
            else:
                # ... otherwise, append to a temporary string
                text_fragment += str_value

    # Merge any remaining collected text into a TextElement
    if text_fragment or len(flat_elements) == 0:
        flat_elements.append(ast.TextElement(text_fragment))

    pattern.elements = flat_elements


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


def _get_default_variant(variants):
    """Return default variant from the list of variants."""
    for variant in variants:
        if variant.default:
            return variant


def _serialize_value(value):
    """Serialize AST values into a simple string."""
    response = ""

    for element in value.elements:
        if isinstance(element, ast.TextElement):
            response += element.value

        elif isinstance(element, ast.Placeable):
            if isinstance(element.expression, ast.SelectExpression):
                default_variant = _get_default_variant(element.expression.variants)
                response += _serialize_value(default_variant.value)
            else:
                response += "{ " + serialize_expression(element.expression) + " }"

    return response


@library.filter
def as_simple_translation(source):
    """Transfrom complex FTL-based strings into single-value strings."""
    translation_ast = parser.parse_entry(source)

    # Non-FTL string or string with an error
    if isinstance(translation_ast, ast.Junk):
        return source

    # Value: use entire AST
    if translation_ast.value:
        tree = translation_ast

    # Attributes (must be present in valid AST if value isn't):
    # use AST of the first attribute
    else:
        tree = translation_ast.attributes[0]

    return _serialize_value(tree.value)


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
