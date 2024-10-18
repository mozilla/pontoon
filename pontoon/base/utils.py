import functools
import re
import time

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape, quoteattr

from guardian.decorators import permission_required as guardian_permission_required

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import make_aware
from django.utils.translation import trans_real


UNUSABLE_SEARCH_CHAR = "☠"


def split_ints(s):
    """Splits string by comma and maps items to the integer."""
    return [int(part) for part in (s or "").split(",") if part]


def get_ip(request):
    try:
        ip = request.META["HTTP_X_FORWARDED_FOR"]
        # If comma-separated list of IPs, take just the last one
        # http://stackoverflow.com/a/18517550
        ip = ip.split(",")[-1]
    except KeyError:
        ip = request.META["REMOTE_ADDR"]

    return ip.strip()


def get_project_locale_from_request(request, locales):
    """Get Pontoon locale from Accept-language request header."""

    header = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    accept = trans_real.parse_accept_lang_header(header)

    for a in accept:
        try:
            return locales.get(code__iexact=a[0]).code
        except BaseException:
            continue


def group_dict_by(list_of_dicts, key):
    """
    Group dicts in a list by the given key. Return a defaultdict instance with
    key used as the key and dict as the value.
    """
    group = defaultdict(list)

    for dictionary in list_of_dicts:
        group[dictionary[key]].append(dictionary)

    return group


def get_object_or_none(model, *args, **kwargs):
    """
    Get an instance of the given model, returning None instead of
    raising an error if an instance cannot be found.
    """
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def is_ajax(request):
    """
    Checks whether the given request is an AJAX request.
    """
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def require_AJAX(f):
    """
    AJAX request required decorator
    """

    @functools.wraps(f)  # Required by New Relic
    def wrap(request, *args, **kwargs):
        if not is_ajax(request):
            return HttpResponseBadRequest("Bad Request: Request must be AJAX")
        return f(request, *args, **kwargs)

    return wrap


def permission_required(perm, *args, **kwargs):
    """Wrapper for guardian permission_required decorator.

    If the request is not permitted and user is anon then it returns 404
    otherwise 403.
    """

    def wrapper(f):
        @functools.wraps(f)
        def wrap(request, *_args, **_kwargs):
            perm_kwargs = (
                dict(return_404=True)
                if request.user.is_anonymous
                else dict(return_403=True)
            )
            perm_kwargs.update(kwargs)
            protected = guardian_permission_required(perm, *args, **perm_kwargs)
            return protected(f)(request, *_args, **_kwargs)

        return wrap

    return wrapper


def aware_datetime(*args, **kwargs):
    """Return an aware datetime using Django's configured timezone."""
    return make_aware(datetime(*args, **kwargs))


def latest_datetime(datetimes):
    """
    Return the latest datetime in the given list of datetimes,
    gracefully handling `None` values in the list. Returns `None` if all
    values in the list are `None`.
    """
    if all(map(lambda d: d is None, datetimes)):
        return None

    min_datetime = make_aware(datetime.min)
    datetimes = map(lambda d: d or min_datetime, datetimes)
    return max(datetimes)


def parse_time_interval(interval):
    """
    Return start and end time objects from time interval string in the format
    %d%m%Y%H%M-%d%m%Y%H%M. Also, increase interval by one minute due to
    truncation to a minute in Translation.counts_per_minute QuerySet.
    """

    def parse_timestamp(timestamp):
        return make_aware(
            datetime.strptime(timestamp, "%Y%m%d%H%M"), timezone=timezone.utc
        )

    start, end = interval.split("-")

    return parse_timestamp(start), parse_timestamp(end) + timedelta(minutes=1)


def convert_to_unix_time(my_datetime):
    """
    Convert datetime object to UNIX time
    """
    return int(time.mktime(my_datetime.timetuple()) * 1000)


def sanitize_xml_input_string(string):
    """
    The XML specification (http://www.w3.org/TR/xml11/#charsets) lists a set of Unicode characters
    that are either illegal or "discouraged". Replace these characters to get valid XML strings
    """

    illegal_xml_chars_re = re.compile(
        "[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]"
    )

    return illegal_xml_chars_re.sub("", string)


def build_translation_memory_file(creation_date, locale_code, entries):
    """
    TMX files will contain large amount of entries and it's impossible to render all the data with
    django templates. Rendering a string in memory is a lot faster.
    :arg datetime creation_date: when TMX file is being created.
    :arg str locale_code: code of a locale
    :arg list entries: A list which contains tuples with following items:
                         * resource_path - path of a resource,
                         * key - key of an entity,
                         * source - source string of entity,
                         * target - translated string,
                         * project_slug - slugified name of a project,
    """
    yield (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '\n<tmx version="1.4">'
        "\n\t<header"
        ' adminlang="en-US"'
        ' creationtoolversion="0.1"'
        ' creationtool="pontoon"'
        ' datatype="plaintext"'
        ' segtype="sentence"'
        ' o-tmf="plain text"'
        ' srclang="en-US"'
        ' creationdate="%(creation_date)s">'
        "\n\t</header>"
        "\n\t<body>" % {"creation_date": creation_date.isoformat()}
    )
    for resource_path, key, source, target, project_slug in entries:
        tuid = ":".join((project_slug, resource_path, slugify(key)))
        source = sanitize_xml_input_string(source)
        target = sanitize_xml_input_string(target)

        yield (
            '\n\t\t<tu tuid=%(tuid)s srclang="en-US">'
            '\n\t\t\t<tuv xml:lang="en-US">'
            "\n\t\t\t\t<seg>%(source)s</seg>"
            "\n\t\t\t</tuv>"
            "\n\t\t\t<tuv xml:lang=%(locale_code)s>"
            "\n\t\t\t\t<seg>%(target)s</seg>"
            "\n\t\t\t</tuv>"
            "\n\t\t</tu>"
            % {
                "tuid": quoteattr(tuid),
                "source": escape(source),
                "locale_code": quoteattr(locale_code),
                "target": escape(target),
            }
        )

    yield ("\n\t</body>" "\n</tmx>\n")


def get_m2m_changes(current_qs, new_qs):
    """
    Get difference between states of a many to many relation.

    :arg django.db.models.QuerySet `current_qs`: objects from the current state of relation.
    :arg django.db.models.QuerySet `final_qs`: objects from the future state of m2m
    :returns: A tuple with 2 querysets for added and removed items from m2m
    """

    add_items = new_qs.exclude(pk__in=current_qs.values_list("pk", flat=True))

    remove_items = current_qs.exclude(pk__in=new_qs.values_list("pk", flat=True))

    return list(add_items), list(remove_items)


def readonly_exists(projects, locale):
    """
    :arg list projects: a list of Project instances.
    :arg Locale locale: Locale instance.
    :returns: True if a read-only ProjectLocale instance for given Projects and
        Locale exists.
    """
    # Avoid circular import; someday we should refactor to avoid.
    from pontoon.base.models import ProjectLocale

    if not isinstance(projects, (QuerySet, tuple, list)):
        projects = [projects]

    return ProjectLocale.objects.filter(
        project__in=projects,
        locale=locale,
        readonly=True,
    ).exists()


def get_search_phrases(search):
    """
    Split the search phrase into separate search queries.
    When the user types a search query without the quotation, e.g.:
    source file
    The function splits it into separate search queries:
    ["source", "file"]
    It works like OR operator, the search engine is going to search for "source" and "file" in a string.

    When the user types a quoted search query, e.g.:
    "source file"
    The function is going to use the full phrase without splitting into separate search queries.
    It works like AND operator, the search engine is going to search for "source file" in a string.

    :arg str search: search query, e.g. source file, "source file"
    :returns: A list of substrings to search.
    """
    search_list = [
        x.strip('"').replace(UNUSABLE_SEARCH_CHAR, '"')
        for x in re.findall(
            '([^"]\\S*|".+?")\\s*', search.replace('\\"', UNUSABLE_SEARCH_CHAR)
        )
    ]

    # Search for `""` and `"` when entered as search terms
    if search == '""' and not search_list:
        search_list = ['""']

    if search == '"' and not search_list:
        search_list = ['"']

    return search_list


def is_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def get_project_or_redirect(
    slug, redirect_view_name, slug_arg_name, request_user, **kwargs
):
    """
    Attempts to get a project with the given slug. If the project doesn't exist, it checks if the slug is in the
    ProjectSlugHistory and if so, it redirects to the current project slug URL. If the old slug is not found in the
    history, it raises an Http404 error.
    """
    # Avoid circular import; someday we should refactor to avoid.
    from pontoon.base.models import Project, ProjectSlugHistory

    try:
        project = Project.objects.visible_for(request_user).available().get(slug=slug)
        return project
    except Project.DoesNotExist:
        slug_history = (
            ProjectSlugHistory.objects.filter(old_slug=slug)
            .order_by("-created_at")
            .first()
        )
        if slug_history is not None:
            redirect_kwargs = {slug_arg_name: slug_history.project.slug}
            redirect_kwargs.update(kwargs)
            redirect_url = reverse(redirect_view_name, kwargs=redirect_kwargs)
            return redirect(redirect_url)
        else:
            raise Http404


def get_locale_or_redirect(code, redirect_view_name=None, url_arg_name=None, **kwargs):
    """
    Attempts to retrieve a locale using the given code. If the locale does not exist, it checks the LocaleCodeHistory
    for a record of the old code. If an entry is found, it either redirects to the view specified by redirect_view_name
    using the new locale code or returns the Locale object if no redirect_view_name is provided.
    The url_arg_name parameter specifies the argument name for the locale code used in the URL pattern of the redirect view.
    If the old code is not found in the history, it raises an Http404 error.
    """
    # Avoid circular import; someday we should refactor to avoid.
    from pontoon.base.models import Locale, LocaleCodeHistory

    try:
        return Locale.objects.get(code=code)
    except Locale.DoesNotExist:
        code_history = (
            LocaleCodeHistory.objects.filter(old_code=code)
            .order_by("-created_at")
            .first()
        )
    if code_history:
        if not redirect_view_name or not url_arg_name:
            return code_history.locale

        redirect_kwargs = {url_arg_name: code_history.locale.code}
        redirect_kwargs.update(kwargs)
        redirect_url = reverse(redirect_view_name, kwargs=redirect_kwargs)
        return redirect(redirect_url)

    raise Http404
