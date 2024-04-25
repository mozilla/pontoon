import codecs
import functools
import io
import os
import re

import requests
import tempfile
import time
import zipfile

from collections import defaultdict
from datetime import datetime, timedelta
from guardian.decorators import permission_required as guardian_permission_required
from urllib.parse import urljoin
from xml.sax.saxutils import escape, quoteattr

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Prefetch, Q
from django.db.models.query import QuerySet
from django.http import HttpResponseBadRequest, Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import trans_real

UNUSABLE_SEARCH_CHAR = "☠"


def split_ints(s):
    """Splits string by comma and maps items to the integer."""
    return [int(part) for part in (s or "").split(",") if part]


def get_project_locale_from_request(request, locales):
    """Get Pontoon locale from Accept-language request header."""

    header = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    accept = trans_real.parse_accept_lang_header(header)

    for a in accept:
        try:
            return locales.get(code__iexact=a[0]).code
        except BaseException:
            continue


def first(collection, test, default=None):
    """
    Return the first item that, when passed to the given test function,
    returns True. If no item passes the test, return the default value.
    """
    return next((c for c in collection if test(c)), default)


def match_attr(collection, **attributes):
    """
    Return the first item that has matching values for the given
    attributes, or None if no item is found to match.
    """
    return first(
        collection,
        lambda i: all(
            getattr(i, attrib) == value for attrib, value in attributes.items()
        ),
        default=None,
    )


def group_dict_by(list_of_dicts, key):
    """
    Group dicts in a list by the given key. Return a defaultdict instance with
    key used as the key and dict as the value.
    """
    group = defaultdict(list)

    for dictionary in list_of_dicts:
        group[dictionary[key]].append(dictionary)

    return group


def extension_in(filename, extensions):
    """
    Check if the extension for the given filename is in the list of
    allowed extensions. Uses os.path.splitext rules for getting the
    extension.
    """
    filename, extension = os.path.splitext(filename)
    if extension and extension[1:] in extensions:
        return True
    else:
        return False


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


def _download_file(prefixes, dirnames, vcs_project, relative_path):
    for prefix in prefixes:
        for dirname in dirnames:
            if vcs_project.configuration:
                locale = vcs_project.locales[0]
                absolute_path = os.path.join(
                    vcs_project.source_directory_path, relative_path
                )
                absolute_l10n_path = vcs_project.configuration.l10n_path(
                    locale, absolute_path
                )
                relative_l10n_path = os.path.relpath(
                    absolute_l10n_path,
                    vcs_project.locale_directory_paths[locale.code],
                )
                url = urljoin(prefix, relative_l10n_path)
            else:
                url = os.path.join(prefix.format(locale_code=dirname), relative_path)

            r = requests.get(url, stream=True)
            if not r.ok:
                continue

            extension = os.path.splitext(relative_path)[1]
            with tempfile.NamedTemporaryFile(
                prefix="strings" if extension == ".xml" else "",
                suffix=extension,
                delete=False,
            ) as temp:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        temp.write(chunk)
                temp.flush()

            return temp.name


def get_download_content(slug, code, part):
    """
    Get content of the file to be downloaded.

    :arg str slug: Project slug.
    :arg str code: Locale code.
    :arg str part: Resource path.
    """
    # Avoid circular import; someday we should refactor to avoid.
    from pontoon.sync import formats
    from pontoon.sync.utils import source_to_locale_path
    from pontoon.sync.vcs.project import VCSProject
    from pontoon.base.models import Entity, Locale, Project, Resource

    project = get_object_or_404(Project, slug=slug)
    locale = get_object_or_404(Locale, code=code)
    vcs_project = VCSProject(project, locales=[locale])

    # Download a ZIP of all files if project has > 1 and < 10 resources
    resources = Resource.objects.filter(
        project=project, translatedresources__locale=locale
    )
    isZipable = 1 < len(resources) < 10
    if isZipable:
        s = io.BytesIO()
        zf = zipfile.ZipFile(s, "w")

    # Download a single file if project has 1 or >= 10 resources
    else:
        resources = [get_object_or_404(Resource, project__slug=slug, path=part)]

    locale_prefixes = project.repositories

    if not project.configuration_file:
        locale_prefixes = locale_prefixes.filter(
            permalink_prefix__contains="{locale_code}"
        )

    locale_prefixes = locale_prefixes.values_list(
        "permalink_prefix", flat=True
    ).distinct()

    source_prefixes = project.repositories.values_list(
        "permalink_prefix", flat=True
    ).distinct()

    for resource in resources:
        # Get locale file
        dirnames = {locale.code, locale.code.replace("-", "_")}
        locale_path = _download_file(
            locale_prefixes, dirnames, vcs_project, resource.path
        )
        if not locale_path and not resource.is_asymmetric:
            return None, None

        # Get source file if needed
        source_path = None
        if resource.is_asymmetric or resource.format == "xliff":
            dirnames = VCSProject.SOURCE_DIR_NAMES
            source_path = _download_file(
                source_prefixes, dirnames, vcs_project, resource.path
            )
            if not source_path:
                return None, None

            # If locale file doesn't exist, create it
            if not locale_path:
                extension = os.path.splitext(resource.path)[1]
                with tempfile.NamedTemporaryFile(
                    prefix="strings" if extension == ".xml" else "",
                    suffix=extension,
                    delete=False,
                ) as temp:
                    temp.flush()
                locale_path = temp.name

        # Update file from database
        resource_file = formats.parse(locale_path, source_path)
        entities_dict = {}
        entities_qs = Entity.objects.filter(
            changedentitylocale__locale=locale,
            resource__project=project,
            resource__path=resource.path,
            obsolete=False,
        )

        for e in entities_qs:
            entities_dict[e.key] = e.translation_set.filter(
                Q(approved=True) | Q(pretranslated=True)
            ).filter(locale=locale)

        for vcs_translation in resource_file.translations:
            key = vcs_translation.key
            if key in entities_dict:
                entity = entities_dict[key]
                vcs_translation.update_from_db(entity)

        resource_file.save(locale)

        if not locale_path:
            return None, None

        if isZipable:
            zf.write(locale_path, source_to_locale_path(resource.path))
        else:
            with codecs.open(locale_path, "r", "utf-8") as f:
                content = f.read()
            filename = os.path.basename(source_to_locale_path(resource.path))

        # Remove temporary files
        os.remove(locale_path)
        if source_path:
            os.remove(source_path)

    if isZipable:
        zf.close()
        content = s.getvalue()
        filename = project.slug + ".zip"

    return content, filename


def handle_upload_content(slug, code, part, f, user):
    """
    Update translations in the database from uploaded file.

    :arg str slug: Project slug.
    :arg str code: Locale code.
    :arg str part: Resource path.
    :arg UploadedFile f: UploadedFile instance.
    :arg User user: User uploading the file.
    """
    # Avoid circular import; someday we should refactor to avoid.
    from pontoon.sync import formats
    from pontoon.sync.changeset import ChangeSet
    from pontoon.sync.vcs.project import VCSProject
    from pontoon.base.models import (
        Entity,
        Locale,
        Project,
        Resource,
        TranslatedResource,
        Translation,
    )

    project = get_object_or_404(Project, slug=slug)
    locale = get_object_or_404(Locale, code=code)
    resource = get_object_or_404(Resource, project__slug=slug, path=part)
    # Store uploaded file to a temporary file and parse it
    extension = os.path.splitext(f.name)[1]
    is_messages_json = f.name.endswith("messages.json")

    with tempfile.NamedTemporaryFile(
        prefix="strings" if extension == ".xml" else "",
        suffix=".messages.json" if is_messages_json else extension,
    ) as temp:
        for chunk in f.chunks():
            temp.write(chunk)
        temp.flush()
        resource_file = formats.parse(temp.name)

    # Update database objects from file
    changeset = ChangeSet(
        project, VCSProject(project, locales=[locale]), timezone.now()
    )
    entities_qs = (
        Entity.objects.filter(
            resource__project=project, resource__path=part, obsolete=False
        )
        .prefetch_related(
            Prefetch(
                "translation_set",
                queryset=Translation.objects.filter(locale=locale),
                to_attr="db_translations",
            )
        )
        .prefetch_related(
            Prefetch(
                "translation_set",
                queryset=Translation.objects.filter(
                    locale=locale, approved_date__lte=timezone.now()
                ),
                to_attr="db_translations_approved_before_sync",
            )
        )
    )
    entities_dict = {entity.key: entity for entity in entities_qs}

    for vcs_translation in resource_file.translations:
        key = vcs_translation.key
        if key in entities_dict:
            entity = entities_dict[key]
            changeset.update_entity_translations_from_vcs(
                entity,
                locale.code,
                vcs_translation,
                user,
                entity.db_translations,
                entity.db_translations_approved_before_sync,
            )

    changeset.bulk_create_translations()
    changeset.bulk_update_translations()
    changeset.bulk_log_actions()

    if changeset.changed_translations:
        # Update 'active' status of all changed translations and their siblings,
        # i.e. translations of the same entity to the same locale.
        changed_pks = {t.pk for t in changeset.changed_translations}
        (
            Entity.objects.filter(
                translation__pk__in=changed_pks
            ).reset_active_translations(locale=locale)
        )

        # Run checks and create TM entries for translations that pass them
        valid_translations = changeset.bulk_check_translations()
        changeset.bulk_create_translation_memory_entries(valid_translations)

        # Remove any TM entries of translations that got rejected
        changeset.bulk_remove_translation_memory_entries()

    TranslatedResource.objects.get(resource=resource, locale=locale).calculate_stats()

    # Mark translations as changed
    changed_translations_pks = [t.pk for t in changeset.changed_translations]
    changed_translations = Translation.objects.filter(pk__in=changed_translations_pks)
    changed_translations.bulk_mark_changed()

    # Update latest translation
    if changeset.translations_to_create:
        changeset.translations_to_create[-1].update_latest_translation()


def aware_datetime(*args, **kwargs):
    """Return an aware datetime using Django's configured timezone."""
    return timezone.make_aware(datetime(*args, **kwargs))


def latest_datetime(datetimes):
    """
    Return the latest datetime in the given list of datetimes,
    gracefully handling `None` values in the list. Returns `None` if all
    values in the list are `None`.
    """
    if all(map(lambda d: d is None, datetimes)):
        return None

    min_datetime = timezone.make_aware(datetime.min)
    datetimes = map(lambda d: d or min_datetime, datetimes)
    return max(datetimes)


def parse_time_interval(interval):
    """
    Return start and end time objects from time interval string in the format
    %d%m%Y%H%M-%d%m%Y%H%M. Also, increase interval by one minute due to
    truncation to a minute in Translation.counts_per_minute QuerySet.
    """

    def parse_timestamp(timestamp):
        return timezone.make_aware(
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
        "[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]"
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
