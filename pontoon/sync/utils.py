from os.path import basename, join
from tempfile import TemporaryDirectory

from moz.l10n.resource import serialize_resource

from django.core.files import File
from django.db.models import Q
from django.utils import timezone

from pontoon.base.badge_utils import badges_review_level, badges_translation_level
from pontoon.base.models import (
    ChangedEntityLocale,
    Locale,
    Project,
    Resource as DbResource,
    Translation,
    User,
)
from pontoon.messaging.notifications import send_badge_notification
from pontoon.sync.core.paths import UploadPaths
from pontoon.sync.core.stats import update_stats
from pontoon.sync.core.translations_from_repo import find_db_updates, write_db_updates
from pontoon.sync.core.translations_to_repo import (
    build_moz_l10n_resource,
    build_translated_resource,
)


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


def import_uploaded_file(
    project: Project, locale: Locale, res_path: str, upload: File, user: User
):
    """Update translations in the database from an uploaded file."""

    with TemporaryDirectory() as root:
        file_path = join(root, basename(res_path))
        with open(file_path, "wb") as file:
            for chunk in upload.chunks():
                file.write(chunk)
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
    else:
        raise Exception("Upload failed.")
