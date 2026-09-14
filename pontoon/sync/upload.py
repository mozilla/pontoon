from dataclasses import dataclass, field
from itertools import groupby
from os.path import basename, join
from tempfile import TemporaryDirectory

from moz.l10n.model import Id as L10nId
from moz.l10n.resource import parse_resource

from django.core.files import File
from django.db.models import Q, prefetch_related_objects
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Locale,
    Project,
    Resource as DbResource,
    Translation,
    User,
)
from pontoon.checks.libraries import run_checks
from pontoon.sync.core.stats import update_stats
from pontoon.sync.core.translations_from_repo import (
    Updates,
    build_translation,
    translations_equal,
    write_db_updates,
)
from pontoon.sync.formats import RepoTranslation, as_repo_translations


class UploadError(Exception):
    """The uploaded file could not be imported; nothing was written to the database."""


class UploadConflictError(Exception):
    """A concurrent change modified translations targeted by the upload."""


@dataclass
class UploadResult:
    """
    Summary of an uploaded file import:
    - `updated`: translations added or replaced
    - `unchanged`: translations identical to the current approved, pretranslated or
      fuzzy one
    - `undefined_keys`: keys of translations with no matching entity in Pontoon
    """

    updated: int = 0
    unchanged: int = 0
    undefined_keys: list[L10nId] = field(default_factory=list)

    @property
    def undefined(self) -> int:
        return len(self.undefined_keys)


def parse_uploaded_file(
    locale: Locale, db_res: DbResource, upload: File
) -> dict[L10nId, RepoTranslation]:
    """Translations in an uploaded file, keyed by entity key."""
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
            raise UploadError(f"Could not parse uploaded file: {error}") from error
    upload_translations = {rt.key: rt for rt in as_repo_translations(l10n_res)}
    if not upload_translations:
        raise UploadError("No translations found in uploaded file.")
    return upload_translations


def entity_ids(db_res: DbResource) -> dict[L10nId, int]:
    """Ids of the resource's current entities, keyed by entity key."""
    return {
        tuple(key): id
        for id, key in Entity.objects.filter(resource=db_res, obsolete=False)
        .values_list("id", "key")
        .iterator()
    }


def parse_upload_for_entities(
    locale: Locale, db_res: DbResource, upload: File
) -> tuple[dict[L10nId, RepoTranslation], dict[L10nId, int], list[L10nId]]:
    """Uploaded translations with a matching entity, the entity ids, and the other keys."""
    upload_translations = parse_uploaded_file(locale, db_res, upload)
    entities = entity_ids(db_res)
    undefined_keys = [key for key in upload_translations if key not in entities]
    for key in undefined_keys:
        del upload_translations[key]
    return upload_translations, entities, undefined_keys


def import_uploaded_file(
    project: Project,
    locale: Locale,
    db_res: DbResource,
    upload: File,
    user: User,
) -> UploadResult:
    """Update translations in the database from an uploaded file."""
    result = UploadResult()
    upload_translations, entities, result.undefined_keys = parse_upload_for_entities(
        locale, db_res, upload
    )

    current_translations = (
        Translation.objects.filter(
            entity__resource=db_res, entity__obsolete=False, locale=locale
        )
        .filter(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
        .values_list("entity__key", "value", "properties", "fuzzy")
        .iterator()
    )
    for key, value, properties, fuzzy in current_translations:
        rt = upload_translations.get(tuple(key), None)
        if (
            rt is not None
            and (rt.fuzzy or not fuzzy)
            and translations_equal(rt.value, rt.properties, value, properties)
        ):
            del upload_translations[rt.key]
            result.unchanged += 1

    updates: Updates = {
        (entities[key], locale.pk): rt for key, rt in upload_translations.items()
    }
    result.updated = len(updates)
    if updates:
        now = timezone.now()
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
    return result


@dataclass
class FailedCheck:
    """An uploaded translation left out because it fails checks."""

    key: L10nId
    errors: list[str]
    warnings: list[str]


@dataclass
class PretranslationUploadResult:
    """
    Summary of an uploaded pretranslation file import:
    - `created`: number of pretranslations added for strings with
      no pretranslation or fuzzy translation
    - `replaced`: number of pretranslations replacing a previous,
      different pretranslation or fuzzy translation
    - `converted`: number of existing translations made the
      active pretranslation, as they match the uploaded translation
    - `unchanged`: number of translations identical to the current pretranslation
    - `skipped`: number of strings left untouched, because they have
      an approved translation or are marked as fuzzy in the uploaded file
    - `failed_checks`: keys of the strings left untouched because the uploaded
      translation fails checks, with the errors and warnings reported for each of them
    - `undefined_keys`: keys of translations with no matching entity in Pontoon
    """

    created: int = 0
    replaced: int = 0
    converted: int = 0
    unchanged: int = 0
    skipped: int = 0
    failed_checks: list[FailedCheck] = field(default_factory=list)
    undefined_keys: list[L10nId] = field(default_factory=list)


@dataclass
class _PendingPretranslation:
    """Changes staged for one entity, applied only if its checks pass."""

    key: L10nId
    match: Translation | None
    new: Translation | None
    reject_ids: list[int]
    deactivate_ids: list[int]
    replaces_translation: bool

    @property
    def translation(self) -> Translation:
        """The row holding the uploaded translation, whether created or matched."""
        return self.new or self.match


def import_uploaded_pretranslations(
    project: Project,
    locale: Locale,
    db_res: DbResource,
    upload: File,
    user: User,
) -> PretranslationUploadResult:
    """
    Store translations from an uploaded file in the database as pretranslations.

    Strings with an approved translation are skipped, so that reviewed translations are
    never replaced. Unlike the built-in pretranslation, strings with unreviewed
    suggestions are pretranslated: a suggestion matching the uploaded translation is
    marked as a pretranslation, keeping its original author, while other suggestions are
    kept as they are. A previous, different pretranslation or fuzzy translation is
    rejected, and a matching one is made the active pretranslation.

    Translations marked as fuzzy in the uploaded file are skipped.

    Uploaded translations that fail any quality check are left out, so that a broken
    translation never replaces a good one. A new pretranslation is not stored, a
    matching one is not converted, and the previous translation stays in place.

    Raises `UploadConflictError` if a review approved a targeted translation after this
    import read it, and that approval was committed first.

    This does not reuse `update_db_translations()`, which has the same overall shape,
    but makes a different call at nearly every decision point:

    |                    | Sync from repo        | Pretranslation upload           |
    | ------------------ | --------------------- | ------------------------------- |
    | Approved           | replaced              | entity skipped                  |
    | Rejects others     | all                   | only pretranslated or fuzzy     |
    | Fuzzy in upload    | stored as fuzzy       | skipped                         |
    | Checks             | after write           | before write, failures dropped  |
    | TM entries         | created               | none                            |
    """
    result = PretranslationUploadResult()
    upload_translations, entities, result.undefined_keys = parse_upload_for_entities(
        locale, db_res, upload
    )

    current: dict[int, list[Translation]] = {
        entity_id: list(txs)
        for entity_id, txs in groupby(
            Translation.objects.filter(
                entity__resource=db_res,
                entity__obsolete=False,
                locale=locale,
                rejected=False,
            )
            .order_by("entity_id")
            .iterator(),
            key=lambda tx: tx.entity_id,
        )
    }

    now = timezone.now()
    pending: list[_PendingPretranslation] = []
    for key, rt in upload_translations.items():
        entity_id = entities[key]
        translations = current.get(entity_id, [])
        if rt.fuzzy or any(tx.approved for tx in translations):
            result.skipped += 1
            continue

        match = next(
            (
                tx
                for tx in translations
                if translations_equal(rt.value, rt.properties, tx.value, tx.properties)
            ),
            None,
        )
        if match is not None and match.pretranslated and match.active:
            result.unchanged += 1
            continue

        reject_ids: list[int] = []
        deactivate_ids: list[int] = []
        for tx in translations:
            if tx is match:
                continue
            if tx.pretranslated or tx.fuzzy:
                reject_ids.append(tx.pk)
            elif tx.active:
                deactivate_ids.append(tx.pk)

        new = None
        if match is None:
            new = build_translation(rt, entity_id, locale.pk, user, now)
            new.pretranslated = True
            new.active = True
        pending.append(
            _PendingPretranslation(
                key=key,
                match=match,
                new=new,
                reject_ids=reject_ids,
                deactivate_ids=deactivate_ids,
                replaces_translation=any(
                    tx.pretranslated or tx.fuzzy for tx in translations
                ),
            )
        )

    # Checks run on the staged translations, before anything is written: a failing
    # upload must not have discarded the translation it would replace. `run_checks()`
    # reports more than `bulk_run_checks()` stores, as only some libraries are saved
    # to the database, so its result is used here rather than the stored rows.
    entities_by_id = {
        entity.pk: entity
        for entity in Entity.objects.filter(
            pk__in={p.translation.entity_id for p in pending}
        )
    }
    if db_res.format == DbResource.Format.DTD:
        # compare-locales needs the other entities of the resource as a reference,
        # and reloads them for each check unless they are cached on `db_res`.
        prefetch_related_objects([db_res], "entities")

    applied: list[_PendingPretranslation] = []
    for p in pending:
        entity = entities_by_id[p.translation.entity_id]
        entity.resource = db_res
        failed = run_checks(entity, locale.code, p.translation.string, False)
        if failed:
            result.failed_checks.append(
                FailedCheck(
                    key=p.key,
                    errors=[m for g, ms in failed.items() if "Errors" in g for m in ms],
                    warnings=[
                        m for g, ms in failed.items() if "Warnings" in g for m in ms
                    ],
                )
            )
        else:
            applied.append(p)

    for p in applied:
        if p.match is not None:
            result.converted += 1
            p.match.pretranslated = True
            p.match.fuzzy = False
            p.match.active = True
        elif p.replaces_translation:
            result.replaced += 1
        else:
            result.created += 1

    reject_ids = [pk for p in applied for pk in p.reject_ids]
    deactivate_ids = [pk for p in applied for pk in p.deactivate_ids]
    converted_translations = [p.match for p in applied if p.match is not None]
    new_translations = [p.new for p in applied if p.new is not None]

    actions: list[ActionLog] = []
    # Rejections and deactivations must be written before translations are activated,
    # to keep a single active translation per entity and locale.
    if reject_ids:
        rejected = Translation.objects.filter(pk__in=reject_ids)
        actions.extend(
            ActionLog(
                action_type=ActionLog.ActionType.TRANSLATION_REJECTED,
                created_at=now,
                performed_by=user,
                translation=tx,
                is_implicit_action=True,
            )
            for tx in rejected
        )
        # Only approved translations have TM entries, so there are none to remove here.
        rejected.update(
            active=False,
            rejected=True,
            rejected_user=user,
            rejected_date=now,
            pretranslated=False,
            fuzzy=False,
        )
    if deactivate_ids:
        Translation.objects.filter(pk__in=deactivate_ids).update(active=False)
    if converted_translations:
        Translation.objects.bulk_update(
            converted_translations, ["active", "fuzzy", "pretranslated"]
        )
    if new_translations:
        Translation.objects.bulk_create(new_translations)

    # A review may approve or reject one of these translations after `current` was
    # loaded; abort if it did, rolling back the upload. A rejection is only a conflict
    # for converted translations, as the other rejected rows were rejected above.
    converted_ids = [tx.pk for tx in converted_translations]
    modified_ids = reject_ids + deactivate_ids + converted_ids
    if (
        modified_ids
        and Translation.objects.filter(
            Q(pk__in=modified_ids, approved=True)
            | Q(pk__in=converted_ids, rejected=True)
        ).exists()
    ):
        raise UploadConflictError()

    actions.extend(
        ActionLog(
            action_type=ActionLog.ActionType.TRANSLATION_CREATED,
            created_at=now,
            performed_by=user,
            translation=tx,
        )
        for tx in new_translations
    )
    if actions:
        ActionLog.objects.bulk_create(actions)

    if new_translations:
        # bulk_create() skips Translation.save(), which would do this
        new_translations[0].update_latest_translation()

    changed_pks = [tx.pk for tx in new_translations + converted_translations]
    if changed_pks or reject_ids:
        update_stats(project)
        Translation.objects.filter(pk__in=reject_ids + changed_pks).bulk_mark_changed()
    return result
