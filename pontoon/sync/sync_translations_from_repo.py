import logging
from collections.abc import Iterable
from datetime import datetime
from os.path import join, relpath, splitext
from typing import cast

from django.db import transaction
from django.db.models import Q
from django.db.models.manager import BaseManager
from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths, parse_android_locale
from moz.l10n.resource import bilingual_extensions

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Locale,
    Project,
    Resource,
    TranslatedResource,
    Translation,
    TranslationMemoryEntry,
    User,
)
from pontoon.checks import DB_FORMATS
from pontoon.checks.utils import bulk_run_checks
from pontoon.sync.checkouts import Checkout, Checkouts
from pontoon.sync.formats import parse
from pontoon.sync.paths import UploadPaths
from pontoon.sync.vcs.translation import VCSTranslation

log = logging.getLogger(__name__)

Updates = dict[tuple[int, int], tuple[dict[int | None, str], bool]]
""" (entity.id, locale.id) -> (plural_form -> string, fuzzy) """


def sync_translations_from_repo(
    project: Project,
    locale_map: dict[str, Locale],
    checkouts: Checkouts,
    paths: L10nConfigPaths | L10nDiscoverPaths,
    db_changes: BaseManager[ChangedEntityLocale],
    now: datetime,
) -> None:
    co = checkouts.target
    source_paths: set[str] = set(paths.ref_paths) if checkouts.source == co else set()
    delete_removed_bilingual_resources(project, co, paths, source_paths)

    changed_target_paths = (
        path
        for path in (join(co.path, co_rel_path) for co_rel_path in co.changed)
        if path not in source_paths
    )
    updates = find_db_updates(
        project, locale_map, changed_target_paths, paths, db_changes
    )
    if updates:
        user = User.objects.get(username="pontoon-sync")
        write_db_updates(project, updates, user, now)


def write_db_updates(
    project: Project, updates: Updates, user: User, now: datetime
) -> None:
    updated_translations, new_translations = update_db_translations(
        project, updates, user, now
    )
    add_errors(new_translations)
    add_translation_memory_entries(project, new_translations + updated_translations)
    update_stats(updates.keys())


def delete_removed_bilingual_resources(
    project: Project,
    target: Checkout,
    paths: L10nConfigPaths | L10nDiscoverPaths,
    source_paths: set[str],
) -> None:
    rm_t = Q()
    rm_tr = Q()
    removed_target_paths = (
        path
        for path in (join(target.path, co_path) for co_path in target.removed)
        if path not in source_paths and splitext(path)[1] in bilingual_extensions
    )
    for target_path in removed_target_paths:
        ref = paths.find_reference(target_path)
        if ref:
            ref_path, path_vars = ref
            locale_code = get_path_locale(path_vars)
            if locale_code is not None:
                db_path = relpath(ref_path, paths.ref_root)
                if db_path.endswith(".pot"):
                    db_path = db_path[:-1]
                rm_t |= Q(entity__resource__path=db_path, locale__code=locale_code)
                rm_tr |= Q(resource__path=db_path, locale__code=locale_code)
    if rm_t and rm_tr:
        with transaction.atomic():
            Translation.objects.filter(entity__resource__project=project).filter(
                rm_t
            ).delete()
            trans_res = TranslatedResource.objects.filter(
                resource__project=project
            ).filter(rm_tr)
            for tr in trans_res:
                tr.adjust_all_stats(
                    0,
                    -tr.approved_strings,
                    -tr.pretranslated_strings,
                    -tr.strings_with_errors,
                    -tr.strings_with_warnings,
                    -tr.unreviewed_strings,
                )
            trans_res.delete()


def find_db_updates(
    project: Project,
    locale_map: dict[str, Locale],
    changed_target_paths: Iterable[str],
    paths: L10nConfigPaths | L10nDiscoverPaths | UploadPaths,
    db_changes: Iterable[ChangedEntityLocale],
) -> Updates | None:
    """
    `(entity.id, locale.id) -> (plural_form -> string, fuzzy)`

    Translations in changed resources, excluding:
    - Exact matches with previous approved or pretranslated translations
    - Entity/Locale combos for which Pontoon has changes since the last sync
    - Translations for which no matching entity is found
    """
    resource_paths: set[str] = set()
    # {(db_path, locale.id, total_strings)}
    translated_resources: set[tuple[str, int, int]] = set()
    # (db_path, tx.key, locale.id) -> (plural_form -> string, fuzzy)
    translations: dict[tuple[str, str, int], tuple[dict[int | None, str], bool]] = {}
    for target_path in changed_target_paths:
        ref = paths.find_reference(target_path)
        if ref:
            ref_path, path_vars = ref
            lc = get_path_locale(path_vars)
            if lc in locale_map:
                locale = locale_map[lc]
                db_path = relpath(ref_path, paths.ref_root)
                try:
                    res = parse(target_path, ref_path, locale)
                except Exception as error:
                    log.error(
                        f"[{project.slug}:{db_path}, {locale.code}] Skipping resource with parse error: {error}"
                    )
                    continue
                if db_path.endswith(".pot"):
                    db_path = db_path[:-1]
                resource_paths.add(db_path)
                translated_resources.add((db_path, locale.id, len(res.entities)))
                translations.update(
                    ((db_path, tx.key, locale.id), (tx.strings, tx.fuzzy))
                    for tx in cast(list[VCSTranslation], res.translations)
                )
    if not translations:
        return None

    resources: dict[str, Resource] = {
        res.path: res
        for res in Resource.objects.filter(project=project, path__in=resource_paths)
    }

    # Exclude translations for which DB & repo already match
    # TODO: Should be able to use repo diff to identify changed entities and refactor this.
    tr_q = Q()
    for db_path, locale_id, _ in translated_resources:
        res = resources.get(db_path, None)
        if res is not None:
            tr_q |= Q(entity__resource=res, locale_id=locale_id)
    if tr_q:
        for tx in (
            Translation.objects.filter(tr_q)
            .filter(Q(approved=True) | Q(pretranslated=True))
            .values(
                "entity__resource__path",
                "entity__key",
                "entity__string",  # terminology/common and tutorial/playground use string instead of key.
                "locale_id",
                "plural_form",
                "string",
            )
        ):
            key = (
                tx["entity__resource__path"],
                tx["entity__key"] or tx["entity__string"],
                tx["locale_id"],
            )
            if key in translations:
                plural_form = tx["plural_form"]
                strings, _ = translations[key]
                if strings.get(plural_form, None) == tx["string"]:
                    if len(strings) > 1:
                        del strings[plural_form]
                    else:
                        del translations[key]
    if not translations:
        return None

    # If repo and database both have changes, database wins.
    for change in db_changes:
        key = (
            change.entity.resource.path,
            change.entity.key or change.entity.string,
            change.locale_id,
        )
        if key in translations:
            del translations[key]
    if not translations:
        return None

    entity_q = Q()
    for db_path, ent_key, _ in translations:
        entity_q |= Q(resource=resources[db_path]) & (
            Q(key=ent_key) | Q(key="", string=ent_key)
        )
    entities: dict[tuple[str, str], int] = {
        (e["resource__path"], e["key"] or e["string"]): e["id"]
        for e in Entity.objects.filter(entity_q).values(
            "id", "key", "string", "resource__path"
        )
    }
    res: Updates = {}
    for (db_path, ent_key, locale_id), tx in translations.items():
        entity_id = entities.get((db_path, ent_key), None)
        if entity_id is not None:
            res[(entity_id, locale_id)] = tx
    return res


def update_db_translations(
    project: Project,
    repo_translations: Updates,
    user: User,
    now: datetime,
) -> tuple[list[Translation], list[Translation]]:
    if not repo_translations:
        return [], []

    translations_to_reject = Q()
    actions: list[ActionLog] = []

    # Approve matching suggestions
    matching_suggestions_q = Q()
    for (entity_id, locale_id), (strings, _) in repo_translations.items():
        for plural_form, string in strings.items():
            matching_suggestions_q |= Q(
                entity_id=entity_id,
                locale_id=locale_id,
                plural_form=plural_form,
                string=string,
            )
    suggestions = list(
        Translation.objects.filter(matching_suggestions_q).filter(
            approved=False, pretranslated=False
        )
    )
    dirty_fields: set[str] = set()
    approve_count = 0
    for tx in suggestions:
        key = (tx.entity_id, tx.locale_id)
        _, fuzzy = repo_translations[key]
        del repo_translations[key]

        if tx.rejected:
            tx.rejected = False
            tx.unrejected_user = None
            tx.unrejected_date = now
            actions.append(
                ActionLog(
                    action_type=ActionLog.ActionType.TRANSLATION_UNREJECTED,
                    performed_by=user,
                    translation=tx,
                )
            )

        tx.active = True
        tx.fuzzy = fuzzy
        if not fuzzy:
            tx.approved = True
            tx.approved_user = None
            tx.approved_date = now
            tx.pretranslated = False
            tx.unapproved_user = None
            tx.unapproved_date = None
            translations_to_reject |= Q(
                entity=tx.entity, locale=tx.locale, plural_form=tx.plural_form
            ) & ~Q(id=tx.id)
            actions.append(
                ActionLog(
                    action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
                    performed_by=user,
                    translation=tx,
                )
            )
            approve_count += 1
        dirty_fields.update(tx.get_dirty_fields())
    update_count = (
        Translation.objects.bulk_update(suggestions, list(dirty_fields))
        if dirty_fields
        else 0
    )
    if update_count:
        count = (
            str(approve_count)
            if approve_count == update_count
            else f"{approve_count}/{update_count}"
        )
        log.info(f"[{project.slug}] Approved {count} translation(s) from repo changes")

    if repo_translations:
        # Add new approved translations for the remainder
        new_translations: list[Translation] = []
        for (entity_id, locale_id), (strings, fuzzy) in repo_translations.items():
            for plural_form, string in strings.items():
                # Note: no tx.entity.resource, which would be required by tx.save()
                tx = Translation(
                    entity_id=entity_id,
                    locale_id=locale_id,
                    string=string,
                    plural_form=plural_form,
                    date=now,
                    active=True,
                )
                if fuzzy:
                    tx.fuzzy = True
                else:
                    tx.approved = True
                    tx.approved_date = now
                new_translations.append(tx)
                actions.append(
                    ActionLog(
                        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
                        created_at=now,
                        performed_by=user,
                        translation=tx,
                    )
                )
        created = Translation.objects.bulk_create(new_translations)
        for tx in created:
            translations_to_reject |= Q(
                entity_id=tx.entity_id,
                locale_id=tx.locale_id,
                plural_form=tx.plural_form,
            ) & ~Q(id=tx.id)
        if created:
            log.info(
                f"[{project.slug}] Created {len(created)} translation(s) from repo changes"
            )

    if translations_to_reject:
        rejected = Translation.objects.filter(rejected=False).filter(
            translations_to_reject
        )
        actions.extend(
            ActionLog(
                action_type=ActionLog.ActionType.TRANSLATION_REJECTED,
                performed_by=user,
                translation=tx,
            )
            for tx in rejected
        )
        reject_count = rejected.update(
            active=False,
            approved=False,
            approved_user=None,
            approved_date=None,
            rejected=True,
            rejected_user=None,
            rejected_date=now,
            pretranslated=False,
            fuzzy=False,
        )
        if reject_count:
            TranslationMemoryEntry.objects.filter(
                translation__in=[tx.pk for tx in rejected]
            ).delete()
            log.info(
                f"[{project.slug}] Rejected {reject_count} translation(s) from repo changes"
            )

    if actions:
        ActionLog.objects.bulk_create(actions)

    return created, suggestions


def get_path_locale(path_vars: dict[str, str]) -> str | None:
    if "locale" in path_vars:
        return path_vars["locale"]
    elif "android_locale" in path_vars:
        return parse_android_locale(path_vars["android_locale"])
    else:
        return None


def add_errors(translations: list[Translation]) -> None:
    """
    Run checks on all changed translations from supported resources
    """
    if translations:
        # TODO: Resource format should be retained
        checked_translations = Translation.objects.filter(
            pk__in=[tx.pk for tx in translations],
            entity__resource__format__in=DB_FORMATS,
        ).select_related("entity__resource", "locale")
        bulk_run_checks(checked_translations)


def add_translation_memory_entries(
    project: Project,
    translations: list[Translation],
) -> None:
    """
    Create Translation Memory entries for:
        - new approved translations
        - updated translations that are approved and don't have a TM entry yet
    """
    if translations:
        TranslationMemoryEntry.objects.bulk_create(
            TranslationMemoryEntry(
                source=tx.tm_source,
                target=tx.tm_target,
                entity_id=tx.entity_id,
                locale_id=tx.locale_id,
                translation=tx,
                project=project,
            )
            for tx in Translation.objects.filter(
                pk__in=[tx.pk for tx in translations],
                approved=True,
                errors__isnull=True,
                memory_entries__isnull=True,
            )
        )


def update_stats(
    changed_entity_locales: Iterable[tuple[int, int]],  # [(entity.id, locale.id)]
):
    query = Q()
    for entity_id, locale_id in changed_entity_locales:
        query |= Q(resource__entities__id=entity_id, locale_id=locale_id)
    for tr in TranslatedResource.objects.filter(query):
        tr.calculate_stats()
