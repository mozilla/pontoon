from dataclasses import dataclass, field
from os.path import basename, join
from tempfile import TemporaryDirectory

from moz.l10n.model import Id as L10nId
from moz.l10n.resource import parse_resource, serialize_resource

from django.core.files import File
from django.db.models import Q
from django.utils import timezone

from pontoon.base.badge_utils import badges_review_level, badges_translation_level
from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Locale,
    Project,
    Resource as DbResource,
    Translation,
    User,
)
from pontoon.messaging.notifications import send_badge_notification
from pontoon.sync.core.stats import update_stats
from pontoon.sync.core.translations_from_repo import (
    Updates,
    translations_equal,
    write_db_updates,
)
from pontoon.sync.core.translations_to_repo import (
    build_moz_l10n_resource,
    build_translated_resource,
)
from pontoon.sync.formats import as_repo_translations


def serialize_translated_resource(db_res: DbResource, locale: Locale) -> str:
    res = build_moz_l10n_resource(db_res)
    translations = {
        tuple(tx.entity.key): tx
        for tx in Translation.objects.filter(
            entity__obsolete=False,
            entity__resource=db_res,
            locale=locale,
            active=True,
        )
        .filter(
            Q(approved=True)
            | Q(pretranslated=True, warnings__isnull=True)
            | Q(fuzzy=True)
        )
        .select_related("entity")
        .iterator()
    }
    tr_res = build_translated_resource(locale, translations, res)

    lc_plurals = locale.cldr_plurals_list()
    return "".join(serialize_resource(tr_res, gettext_plurals=lc_plurals))


@dataclass
class UploadResult:
    """
    Summary of an uploaded file import:
    - `updated`: translations added or replaced
    - `unchanged`: translations identical to the current approved or pretranslated one
    - `undefined_keys`: keys of translations with no matching entity in Pontoon
    """

    updated: int = 0
    unchanged: int = 0
    undefined_keys: list[L10nId] = field(default_factory=list)
    badge_name: str = ""
    badge_level: int = 0


def import_uploaded_file(
    project: Project,
    locale: Locale,
    db_res: DbResource,
    upload: File,
    user: User,
) -> UploadResult:
    """Update translations in the database from an uploaded file."""
    with TemporaryDirectory() as root:
        file_path = join(root, basename(db_res.path))
        with open(file_path, "wb") as file:
            for chunk in upload.chunks():
                file.write(chunk)
        try:
            l10n_res = parse_resource(
                file_path,
                gettext_plurals=locale.cldr_plurals_list(),
                gettext_skip_obsolete=True,
            )
        except Exception as error:
            raise Exception(f"Could not parse uploaded file: {error}") from error
    upload_translations = {rt.key: rt for rt in as_repo_translations(l10n_res)}
    if not upload_translations:
        raise Exception("No translations found in uploaded file.")

    result = UploadResult()
    entities: dict[L10nId, int] = {
        tuple(key): id
        for id, key in Entity.objects.filter(resource=db_res, obsolete=False)
        .values_list("id", "key")
        .iterator()
    }
    result.undefined_keys = [key for key in upload_translations if key not in entities]
    for key in result.undefined_keys:
        del upload_translations[key]

    current_translations = (
        Translation.objects.filter(
            entity__resource=db_res, entity__obsolete=False, locale=locale
        )
        .filter(Q(approved=True) | Q(pretranslated=True))
        .values_list("entity__key", "value", "properties")
        .iterator()
    )
    for key, value, properties in current_translations:
        rt = upload_translations.get(tuple(key), None)
        if rt is not None and translations_equal(
            rt.value, rt.properties, value, properties
        ):
            del upload_translations[rt.key]
            result.unchanged += 1

    updates: Updates = {
        (entities[key], locale.pk): rt for key, rt in upload_translations.items()
    }
    result.updated = len(updates)
    if updates:
        now = timezone.now()
        translation_before_level = badges_translation_level(user)
        review_before_level = badges_review_level(user)
        # write_db_updates() removes entries from `updates` as it processes them
        update_keys = list(updates)
        write_db_updates(project, updates, user, now)
        update_stats(project)
        ChangedEntityLocale.objects.bulk_create(
            (
                ChangedEntityLocale(entity_id=entity_id, locale_id=locale_id, when=now)
                for entity_id, locale_id in update_keys
            ),
            ignore_conflicts=True,
        )

        if badges_translation_level(user) > translation_before_level:
            result.badge_name = "Translation Champion"
            result.badge_level = badges_translation_level(user)
            send_badge_notification(user, result.badge_name, result.badge_level)
        if badges_review_level(user) > review_before_level:
            result.badge_name = "Review Master"
            result.badge_level = badges_review_level(user)
            send_badge_notification(user, result.badge_name, result.badge_level)
    return result
