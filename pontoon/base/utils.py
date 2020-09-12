from __future__ import absolute_import

import codecs
import functools
import os
import tempfile
import time
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin
from xml.sax.saxutils import escape, quoteattr

import pytz
import requests
from compare_locales.paths.matcher import Variable, Star, Starstar
from django.db.models import Prefetch, Q
from django.db.models.query import QuerySet
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import trans_real
from guardian.decorators import permission_required as guardian_permission_required
from six import BytesIO


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


def aware_datetime(*args, **kwargs):
    """Return an aware datetime using Django's configured timezone."""
    return timezone.make_aware(datetime(*args, **kwargs))


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


def require_AJAX(f):
    """
    AJAX request required decorator
    """

    @functools.wraps(f)  # Required by New Relic
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
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
                url = prefix.format(locale_code=dirname)
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


def _get_relative_path_from_part(slug, part):
    """Check if part is a Resource path or Subpage name."""
    # Avoid circular import; someday we should refactor to avoid.
    from pontoon.base.models import Subpage

    try:
        subpage = Subpage.objects.get(project__slug=slug, name=part)
        return subpage.resources.first().path
    except Subpage.DoesNotExist:
        return part


def config_path_to_urlpath(config_root, checkout_path, path):
    """
    Generate the url path to the resource based on the Project config's l10n path.
    Unfortunately, it's impossible to map some of the Project Config's semantics e.g. Star and StarStar filters,
    because they would need the list of files they match (which may be hard to implement).
    """
    permalink_prefix = os.path.join(config_root.replace(checkout_path, ""), "")

    for part in path["l10n"].pattern:
        if isinstance(part, Variable):
            if part.name in ("android_locale", "locale"):
                permalink_prefix += "{locale_code}"
            else:
                raise ValueError(f"Unsupported Project Config variable: {part.name}")
        elif isinstance(part, (Starstar, Star)):
            raise ValueError("** and * file filters are unsupported")
        else:
            permalink_prefix += part
    return permalink_prefix


def get_permalinks_from_project_config(project, resources):
    """
    Generate the permalinks to the resources based on the configuration of the project.
    """
    from pontoon.sync.vcs.models import DownloadTOMLParser

    checkout_path = os.path.join(
        project.translation_repositories()[0].checkout_path, ""
    )
    source_repository = project.source_repository
    parser = DownloadTOMLParser(
        source_repository.checkout_path,
        source_repository.permalink_prefix,
        project.configuration_file,
    ).parse(env={"l10n_base": checkout_path})

    # In order to reduce the number of HTTP requests, we want to filter the list of permalinks retrieved from
    # the project config files and reduce the list to paths that match the requested resources.
    resources_matchers = []
    for res in resources:
        matcher = str(Path(res.path).parent)

        # @Mathjazz
        # Without this, it's impossible to figure out url paths of the resources on some repos, e.g.:
        # * mozilla-donate-content
        # * thunderbird-donate-content
        # Do you see a better way to handle this?
        if source_repository.source_repo:
            matcher = matcher.replace("templates/", "")

        resources_matchers.append(matcher)

    for pc in parser.configs:
        for path in pc.paths:
            permalink_prefix = config_path_to_urlpath(
                os.path.join(pc.root, ""), checkout_path, path
            )
            if not permalink_prefix:
                continue

            path = urljoin(source_repository.permalink_prefix, permalink_prefix)
            for res_matcher in resources_matchers:
                if res_matcher in path:
                    yield path


def get_download_content(slug, code, part):
    """
    Get content of the file to be downloaded.

    :arg str slug: Project slug.
    :arg str code: Locale code.
    :arg str part: Resource path or Subpage name.
    """
    # Avoid circular import; someday we should refactor to avoid.
    from pontoon.sync import formats
    from pontoon.sync.vcs.models import VCSProject
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
        s = BytesIO()
        zf = zipfile.ZipFile(s, "w")

    # Download a single file if project has 1 or >= 10 resources
    else:
        relative_path = _get_relative_path_from_part(slug, part)
        resources = [
            get_object_or_404(Resource, project__slug=slug, path=relative_path)
        ]

    locale_prefixes = []

    if project.configuration_file:
        locale_prefixes += get_permalinks_from_project_config(project, resources)

    locale_prefixes += list(
        project.repositories.filter(Q(permalink_prefix__contains="{locale_code}"))
        .values_list("permalink_prefix", flat=True)
        .distinct()
    )

    project_config_enabled = bool(project.configuration_file)

    source_prefixes = []

    if project_config_enabled:
        source_prefixes += [
            urljoin(project.source_repository.permalink_prefix, res.path)
            for res in resources
        ]

    source_prefixes += list(
        project.repositories.values_list("permalink_prefix", flat=True).distinct()
    )

    for resource in resources:
        # Get locale file
        dirnames = set([locale.code, locale.code.replace("-", "_")])
        locale_path = _download_file(
            locale_prefixes, dirnames, vcs_project, resource.path
        )
        if not locale_path and not resource.is_asymmetric:
            return None, None

        # Get source file if needed
        source_path = None
        if resource.is_asymmetric:
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
                approved=True, locale=locale
            )

        for vcs_translation in resource_file.translations:
            key = vcs_translation.key
            if key in entities_dict:
                entity = entities_dict[key]
                vcs_translation.update_from_db(entity)

        resource_file.save(locale)

        if not locale_path:
            return None, None

        if isZipable:
            zf.write(locale_path, resource.path)
        else:
            with codecs.open(locale_path, "r", "utf-8") as f:
                content = f.read()
            filename = os.path.basename(resource.path)

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
    :arg str part: Resource path or Subpage name.
    :arg UploadedFile f: UploadedFile instance.
    :arg User user: User uploading the file.
    """
    # Avoid circular import; someday we should refactor to avoid.
    from pontoon.sync import formats
    from pontoon.sync.changeset import ChangeSet
    from pontoon.sync.vcs.models import VCSProject
    from pontoon.base.models import (
        ChangedEntityLocale,
        Entity,
        Locale,
        Project,
        Resource,
        TranslatedResource,
        Translation,
    )

    relative_path = _get_relative_path_from_part(slug, part)
    project = get_object_or_404(Project, slug=slug)
    locale = get_object_or_404(Locale, code=code)
    resource = get_object_or_404(Resource, project__slug=slug, path=relative_path)

    # Store uploaded file to a temporary file and parse it
    extension = os.path.splitext(f.name)[1]
    with tempfile.NamedTemporaryFile(
        prefix="strings" if extension == ".xml" else "", suffix=extension,
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
            resource__project=project, resource__path=relative_path, obsolete=False
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

    TranslatedResource.objects.get(resource=resource, locale=locale).calculate_stats()

    # Mark translations as changed
    changed_entities = {}
    existing = ChangedEntityLocale.objects.values_list("entity", "locale").distinct()
    for t in changeset.changed_translations:
        key = (t.entity.pk, t.locale.pk)
        # Remove duplicate changes to prevent unique constraint violation
        if key not in existing:
            changed_entities[key] = ChangedEntityLocale(
                entity=t.entity, locale=t.locale
            )

    ChangedEntityLocale.objects.bulk_create(changed_entities.values())

    # Update latest translation
    if changeset.translations_to_create:
        changeset.translations_to_create[-1].update_latest_translation()


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
            datetime.strptime(timestamp, "%Y%m%d%H%M"), timezone=pytz.UTC
        )

    start, end = interval.split("-")

    return parse_timestamp(start), parse_timestamp(end) + timedelta(minutes=1)


def convert_to_unix_time(my_datetime):
    """
    Convert datetime object to UNIX time
    """
    return int(time.mktime(my_datetime.timetuple()) * 1000)


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
                         * project_name - name of a project,
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
    for resource_path, key, source, target, project_name, project_slug in entries:
        tuid = ":".join((project_slug, resource_path, slugify(key)))
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
                "project_name": escape(project_name),
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
        project__in=projects, locale=locale, readonly=True,
    ).exists()
