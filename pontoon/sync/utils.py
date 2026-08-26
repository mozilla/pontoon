import logging

from collections import defaultdict
from collections.abc import Iterator
from os.path import basename, commonpath, exists, join, normpath, relpath
from tempfile import TemporaryDirectory

from moz.l10n.resource import parse_resource, serialize_resource

from django.core.files import File
from django.db.models import Q
from django.utils import timezone

from pontoon.base.badge_utils import badges_review_level, badges_translation_level
from pontoon.base.models import (
    ChangedEntityLocale,
    Locale,
    Project,
    Resource,
    Translation,
    User,
)
from pontoon.messaging.notifications import send_badge_notification
from pontoon.sync.core.checkout import checkout_repos
from pontoon.sync.core.paths import UploadPaths, find_paths
from pontoon.sync.core.stats import update_stats
from pontoon.sync.core.translations_from_repo import find_db_updates, write_db_updates
from pontoon.sync.core.translations_to_repo import set_translations


log = logging.getLogger(__name__)


def serialize_locale(
    project: Project, locale: Locale, resource_path: str | None = None
) -> Iterator[tuple[str, str]]:
    """
    Serialize `project` resources translated into `locale` from the database.

    Yields `(path, content)` tuples, where `path` is relative to the target
    repository root, matching the layout produced by two-way sync.
    """
    checkouts = checkout_repos(project, shallow=True)
    paths = find_paths(project, checkouts)
    # Narrowing the paths to a single locale is intentional; per-path locale
    # restrictions from an L10nConfigPaths config are still honored via the
    # locale_codes check below.
    paths.locales = [locale.code]
    ref_root = normpath(paths.ref_root)

    resource_qs = Resource.objects.filter(project=project)
    if resource_path is not None:
        resource_qs = resource_qs.filter(path=resource_path)
    resources = list(resource_qs)

    # Fetch all relevant translations in a single query and group them by
    # resource, rather than querying once per resource (N+1).
    translations_by_resource: dict[int, list[Translation]] = defaultdict(list)
    for tx in (
        Translation.objects.filter(
            entity__obsolete=False,
            entity__resource__in=resources,
            locale=locale,
            active=True,
        )
        .filter(
            Q(approved=True)
            | Q(pretranslated=True, warnings__isnull=True)
            | Q(fuzzy=True)
        )
        .select_related("entity")
    ):
        translations_by_resource[tx.entity.resource_id].append(tx)

    for resource in resources:
        target, locale_codes = paths.target(resource.path)
        if target is None or locale.code not in locale_codes:
            continue
        ref_path = normpath(join(ref_root, resource.path))
        if ref_path.endswith(".po"):
            ref_path += "t"
        # `resource.path` is unrestricted, so a leading "/" or ".." segments
        # could escape the reference root and read arbitrary files; reject it.
        if commonpath((ref_root, ref_path)) != ref_root:
            log.error(f"[{project.slug}:{resource.path}] Invalid resource path")
            continue
        if not exists(ref_path):
            log.error(f"[{project.slug}:{resource.path}] Missing source file")
            continue
        translations = translations_by_resource.get(resource.id, [])
        res = parse_resource(ref_path)
        set_translations(locale, translations, res)
        content = "".join(
            serialize_resource(res, gettext_plurals=locale.cldr_plurals_list())
        )
        target_path = paths.format_target_path(target, locale.code)
        rel_path = relpath(target_path, checkouts.target.path).replace("\\", "/")
        yield rel_path, content


def import_uploaded_file(
    project: Project, locale: Locale, res_path: str, upload: File, user: User
):
    """
    Update translations in the database from an uploaded file.

    Raises an Exception describing why nothing was imported when the upload
    yields no database updates. `find_db_updates()` only logs parse errors and
    returns `None` for both "nothing parsed" and "nothing new", so the file is
    parsed here first to be able to tell the three cases apart.
    """

    with TemporaryDirectory() as root:
        file_path = join(root, basename(res_path))
        with open(file_path, "wb") as file:
            for chunk in upload.chunks():
                file.write(chunk)
        try:
            parse_resource(
                file_path,
                gettext_plurals=locale.cldr_plurals_list(),
                gettext_skip_obsolete=True,
            )
        except Exception as error:
            raise Exception(
                f"Upload failed. Could not parse {basename(res_path)}: {error}"
            )
        paths = UploadPaths(res_path, locale.code, file_path)
        updates = find_db_updates(
            project, {locale.code: locale}, [file_path], paths, []
        )
    if updates:
        now = timezone.now()
        translation_before_level = badges_translation_level(user)
        review_before_level = badges_review_level(user)
        write_db_updates(project, updates, user, now)
        update_stats(project)
        ChangedEntityLocale.objects.bulk_create(
            (
                ChangedEntityLocale(entity_id=entity_id, locale_id=locale_id, when=now)
                for entity_id, locale_id in updates
            ),
            ignore_conflicts=True,
        )

        badge_name = ""
        badge_level = 0
        if badges_translation_level(user) > translation_before_level:
            badge_name = "Translation Champion"
            badge_level = badges_translation_level(user)
            send_badge_notification(user, badge_name, badge_level)
        if badges_review_level(user) > review_before_level:
            badge_name = "Review Master"
            badge_level = badges_review_level(user)
            send_badge_notification(user, badge_name, badge_level)
        return badge_name, badge_level
    elif updates is None:
        raise Exception(
            "Upload failed. No new translations found: every translation in the "
            "uploaded file is already in Pontoon."
        )
    else:
        # The file parsed and holds translations, but none of its keys match a
        # source string of this resource. Source strings come from the project
        # repository, so they cannot be added by uploading a translation file.
        raise Exception(
            f"Upload failed. None of the translations in the uploaded file match a "
            f"source string of {res_path}. New source strings have to be added to "
            f"the project repository first."
        )
