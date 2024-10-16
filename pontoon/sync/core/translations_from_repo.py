import logging

from collections import defaultdict
from collections.abc import Iterable, Sized
from datetime import datetime
from os.path import join, relpath, splitext
from typing import cast

from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths, parse_android_locale
from moz.l10n.resource import bilingual_extensions, l10n_extensions

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.db.models.manager import BaseManager

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
from pontoon.sync.core.checkout import Checkout, Checkouts
from pontoon.sync.core.paths import UploadPaths
from pontoon.sync.formats import parse
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
) -> tuple[int, int]:
    """(removed_count, updated_count)"""
    co = checkouts.target
    source_paths: set[str] = set(paths.ref_paths) if checkouts.source == co else set()
    del_count = delete_removed_bilingual_resources(project, co, paths, source_paths)

    changed_target_paths = [
        path
        for path in (join(co.path, co_rel_path) for co_rel_path in co.changed)
        if path not in source_paths
    ]
    if changed_target_paths:
        n = len(changed_target_paths)
        str_files = "file" if n == 1 else "files"
        log.info(
            f"[{project.slug}] Reading changes from {n} changed target {str_files}"
        )
    updates = find_db_updates(
        project, locale_map, changed_target_paths, paths, db_changes
    )
    if updates:
        user = User.objects.get(username="pontoon-sync")
        write_db_updates(project, updates, user, now)
    return del_count, 0 if updates is None else len(updates)


def write_db_updates(
    project: Project, updates: Updates, user: User, now: datetime
) -> None:
    updated_translations, new_translations = update_db_translations(
        project, updates, user, now
    )
    add_errors(new_translations)
    add_translation_memory_entries(project, new_translations + updated_translations)


def delete_removed_bilingual_resources(
    project: Project,
    target: Checkout,
    paths: L10nConfigPaths | L10nDiscoverPaths,
    source_paths: set[str],
) -> int:
    rm_t = Q()
    rm_tr = Q()
    count = 0
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
                if not project.configuration_file and db_path.endswith(".pot"):
                    db_path = db_path[:-1]
                rm_t |= Q(entity__resource__path=db_path, locale__code=locale_code)
                rm_tr |= Q(resource__path=db_path, locale__code=locale_code)
                count += 1
    if rm_t and rm_tr:
        str_del_resources = "deleted resource" if count == 1 else "deleted resources"
        log.info(f"[{project.slug}] Removing {count} {str_del_resources}")
        with transaction.atomic():
            Translation.objects.filter(entity__resource__project=project).filter(
                rm_t
            ).delete()
            TranslatedResource.objects.filter(resource__project=project).filter(
                rm_tr
            ).delete()
    return count


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
    log.debug(f"[{project.slug}] Scanning for translation updates...")
    resource_paths: set[str] = set()
    # db_path -> {locale.id}
    translated_resources: dict[str, set[int]] = defaultdict(set)
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
                lc_scope = f"[{project.slug}:{db_path}, {locale.code}]"
                try:
                    res = parse(target_path, ref_path, locale)
                except Exception as error:
                    log.error(f"{lc_scope} Skipping resource with parse error: {error}")
                    continue
                if not project.configuration_file and db_path.endswith(".pot"):
                    db_path = db_path[:-1]
                resource_paths.add(db_path)
                translated_resources[db_path].add(locale.id)
                translations.update(
                    ((db_path, tx.key, locale.id), (tx.strings, tx.fuzzy))
                    for tx in cast(list[VCSTranslation], res.translations)
                    if tx.strings
                )
        elif splitext(target_path)[1] in l10n_extensions:
            log.debug(
                f"[{project.slug}:{relpath(target_path, paths.base)}] Not an L10n target path"
            )
    if not translations:
        return None

    resources: dict[str, Resource] = {
        res.path: res
        for res in Resource.objects.filter(
            project=project, path__in=resource_paths
        ).iterator()
    }

    # Exclude translations for which DB & repo already match
    # TODO: Should be able to use repo diff to identify changed entities and refactor this.
    trans_q = Q()
    for db_path, locale_ids in translated_resources.items():
        res = resources.get(db_path, None)
        if res is not None:
            trans_q |= Q(entity__resource=res, locale_id__in=locale_ids)
    if trans_q:
        log.debug(f"[{project.slug}] Filtering matches from translations...")
        trans_query = (
            Translation.objects.filter(trans_q)
            .filter(Q(approved=True) | Q(pretranslated=True))
            .order_by("id")
            .values(
                "entity__resource__path",
                "entity__key",
                "entity__string",  # terminology/common and tutorial/playground use string instead of key.
                "locale_id",
                "plural_form",
                "string",
            )
        )
        paginator = Paginator(trans_query, per_page=10000, allow_empty_first_page=True)
        for page_number in paginator.page_range:
            page = paginator.page(page_number)
            for trans_values in page:
                key = (
                    trans_values["entity__resource__path"],
                    trans_values["entity__key"] or trans_values["entity__string"],
                    trans_values["locale_id"],
                )
                if key in translations:
                    plural_form = trans_values["plural_form"]
                    strings, _ = translations[key]
                    if strings.get(plural_form, None) == trans_values["string"]:
                        if len(strings) > 1:
                            del strings[plural_form]
                        else:
                            del translations[key]
            if paginator.num_pages > 3:
                log.debug(
                    f"[{project.slug}] Filtering matches from translations... {page_number}/{paginator.num_pages}"
                )
    if not translations:
        return None

    # If repo and database both have changes, database wins.
    log.debug(f"[{project.slug}] Filtering db changes from translations...")
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

    log.debug(f"[{project.slug}] Compiling updates...")
    trans_res = {resources[db_path] for db_path, _, _ in translations}
    entities: dict[tuple[str, str], int] = {
        (e["resource__path"], e["key"] or e["string"]): e["id"]
        for e in Entity.objects.filter(resource__in=trans_res, obsolete=False)
        .values("id", "key", "string", "resource__path")
        .iterator()
    }
    res: Updates = {}
    for (db_path, ent_key, locale_id), tx in translations.items():
        entity_id = entities.get((db_path, ent_key), None)
        if entity_id is not None:
            res[(entity_id, locale_id)] = tx
    log.debug(f"[{project.slug}] Compiling updates... Found {len(res)}")
    return res


def update_db_translations(
    project: Project,
    repo_translations: Updates,
    user: User,
    now: datetime,
) -> tuple[list[Translation], list[Translation]]:
    if not repo_translations:
        return [], []
    log.debug(f"[{project.slug}] Syncing translations from repo...")

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
    if matching_suggestions_q:
        # (entity_id, locale_id, plural_form) => translation
        suggestions: dict[tuple[int, int, int], Translation] = {
            (tx.entity_id, tx.locale_id, tx.plural_form): tx
            for tx in Translation.objects.filter(matching_suggestions_q)
            .filter(approved=False, pretranslated=False)
            .iterator()
        }
    else:
        log.warning(
            f"[{project.slug}] Empty strings in repo_translations!? {repo_translations}"
        )
        suggestions = {}
    update_fields: set[str] = set()
    approve_count = 0
    for tx in suggestions.values():
        _, fuzzy = repo_translations[(tx.entity_id, tx.locale_id)]

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
            actions.append(
                ActionLog(
                    action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
                    performed_by=user,
                    translation=tx,
                )
            )
            approve_count += 1
        translations_to_reject |= Q(
            entity=tx.entity, locale=tx.locale, plural_form=tx.plural_form
        )
        update_fields.update(tx.get_dirty_fields())
    for entity_id, locale_id, _ in suggestions:
        try:
            del repo_translations[(entity_id, locale_id)]
        except KeyError:
            pass

    new_translations: list[Translation] = []
    if repo_translations:
        # Add new approved translations for the remainder
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
                translations_to_reject |= Q(
                    entity_id=entity_id, locale_id=locale_id, plural_form=plural_form
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
                f"[{project.slug}] Rejected {str_n_translations(reject_count)} from repo changes"
            )

    update_count = (
        Translation.objects.bulk_update(suggestions.values(), list(update_fields))
        if update_fields
        else 0
    )
    if update_count:
        count = (
            str(approve_count)
            if approve_count == update_count
            else f"{approve_count}/{update_count}"
        )
        log.info(
            f"[{project.slug}] Approved {str_n_translations(count)} from repo changes"
        )

    created = Translation.objects.bulk_create(new_translations)
    if created:
        log.info(
            f"[{project.slug}] Created {str_n_translations(created)} from repo changes"
        )

    if actions:
        ActionLog.objects.bulk_create(actions)

    return created, list(suggestions.values())


def str_n_translations(n: int | Sized) -> str:
    if not isinstance(n, int):
        n = len(n)
    return "1 translation" if n == 1 else f"{n} translations"


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
            ).iterator()
        )
