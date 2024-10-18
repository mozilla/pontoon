import logging

from collections import defaultdict
from collections.abc import Container
from datetime import datetime
from os import remove
from os.path import commonpath, isfile, join, normpath

from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths

from django.conf import settings
from django.db.models import Q
from django.db.models.manager import BaseManager

from pontoon.base.models import Locale, Project, Translation, User
from pontoon.base.models.changed_entity_locale import ChangedEntityLocale
from pontoon.sync.core.checkout import Checkouts
from pontoon.sync.formats import parse
from pontoon.sync.formats.po import POResource
from pontoon.sync.repositories import CommitToRepositoryException, get_repo


log = logging.getLogger(__name__)


def sync_translations_to_repo(
    project: Project,
    commit: bool,
    locale_map: dict[str, Locale],
    checkouts: Checkouts,
    paths: L10nConfigPaths | L10nDiscoverPaths,
    db_changes: BaseManager[ChangedEntityLocale],
    changed_source_paths: set[str],
    removed_source_paths: set[str],
    now: datetime,
) -> None:
    readonly_locales = project.locales.filter(project_locale__readonly=True)
    removed = delete_removed_resources(
        project, paths, locale_map, readonly_locales, removed_source_paths
    )
    updated, updated_locales, translators = update_changed_resources(
        project,
        paths,
        locale_map,
        readonly_locales,
        db_changes,
        changed_source_paths,
        now,
    )
    if not removed and not updated:
        return

    if not commit:
        log.info(f"[{project.slug}] Skipping commit & push")
        return

    if removed:
        lc_str = "all localizations"
    else:
        if len(updated_locales) > 4:
            lc_str = f"{len(updated_locales)} localizations"
        else:
            lc_str = ", ".join(f"{loc.name} ({loc.code})" for loc in updated_locales)
    commit_msg = f"Pontoon/{project.name}: Update {lc_str}"

    if translators:
        commit_msg += "\n"
        for translator, lc_set in translators.items():
            tr_str = translator.display_name_and_email
            lc_str = ", ".join(sorted(lc_set))
            commit_msg += f"\nCo-authored-by: {tr_str} ({lc_str})"

    commit_author = f"{settings.VCS_SYNC_NAME} <{settings.VCS_SYNC_EMAIL}>"

    co = checkouts.target
    repo = get_repo(co.repo.type)
    try:
        repo.commit(co.path, commit_msg, commit_author, co.repo.branch, co.url)
        co.commit = repo.revision(co.path)
    except CommitToRepositoryException as error:
        log.warning(f"[{project.slug}] {co.repo.type} commit failed: {error}")
        raise error


def delete_removed_resources(
    project: Project,
    paths: L10nConfigPaths | L10nDiscoverPaths,
    locale_map: dict[str, Locale],
    readonly_locales: BaseManager[Locale],
    removed_source_paths: set[str],
) -> int:
    count = 0
    for path in removed_source_paths:
        log_scope = f"[{project.slug}:{path}]"
        log.info(f"{log_scope} Removing for all locales")
        target, locale_codes = paths.target(path)
        if target and commonpath((paths.base, target)) == paths.base:
            for lc in locale_codes:
                if lc not in locale_map or locale_map[lc] in readonly_locales:
                    continue
                target_path = paths.format_target_path(target, lc)
                try:
                    remove(target_path)
                    count += 1
                except FileNotFoundError:
                    pass
        else:
            log.error(f"{log_scope} Invalid resource path")
    return count


def update_changed_resources(
    project: Project,
    paths: L10nConfigPaths | L10nDiscoverPaths,
    locale_map: dict[str, Locale],
    readonly_locales: Container[Locale],
    db_changes: BaseManager[ChangedEntityLocale],
    changed_source_paths: set[str],
    now: datetime,
) -> tuple[int, set[Locale], dict[User, set[str]]]:
    count = 0
    # db_path -> [Locale], empty list stands for "all locales"
    changed_resources: dict[str, list[Locale]] = {
        path: [] for path in changed_source_paths
    }
    for change in db_changes:
        if change.locale in readonly_locales:
            continue
        path = str(change.entity.resource.path)
        if path not in changed_resources:
            changed_resources[path] = [change.locale]
        else:
            prev = changed_resources[path]
            if prev:
                prev.append(change.locale)
    changed_entities = set(change.entity for change in db_changes)
    if changed_resources:
        n = len(changed_resources)
        str_resources = "resource" if n == 1 else "resources"
        log.info(f"[{project.slug}] Updating {n} changed {str_resources}")

    updated_locales: set[Locale] = set()
    translators: dict[User, set[str]] = defaultdict(set)
    for path, locales_ in changed_resources.items():
        log_scope = f"[{project.slug}:{path}]"
        target, locale_codes = paths.target(path)
        if target is None:
            continue
        if commonpath((paths.base, target)) != paths.base:
            log.error(f"{log_scope} Invalid resource path")
            continue
        locales = locales_ or [
            locale
            for locale in (
                locale_map[lc] for lc in sorted(locale_codes) if lc in locale_map
            )
            if locale not in readonly_locales
        ]
        if not locales:
            continue
        ref_path = normpath(join(paths.ref_root, path))
        if ref_path.endswith(".po"):
            ref_path += "t"
        if not isfile(ref_path):
            log.error(f"{log_scope} Missing source file")
            continue
        if locales_:
            lc_str = ", ".join(locale.code for locale in locales_)
            log.info(f"{log_scope} Updating locales: {lc_str}")
        else:
            log.info(f"{log_scope} Updating all locales")

        translations = (
            Translation.objects.filter(
                entity__obsolete=False,
                entity__resource__project_id=project.pk,
                entity__resource__path=path,
                locale__in=[locale.pk for locale in locales],
            )
            .filter(Q(approved=True) | Q(pretranslated=True))
            .exclude(approved_date__gt=now)  # includes approved_date = None
            .select_related("entity")
        )
        for locale in locales:
            lc_scope = f"[{project.slug}:{path}, {locale.code}]"
            lc_translations = [tx for tx in translations if tx.locale_id == locale.pk]
            target_path = paths.format_target_path(target, locale.code)
            if not lc_translations and not isfile(target_path):
                continue
            try:
                res = parse(target_path, ref_path, locale)
                if isinstance(res, POResource):
                    for po_ent in res.entities:
                        po_tx = [
                            tx for tx in lc_translations if tx.entity.key == po_ent.key
                        ]
                        po_ent.strings = {tx.plural_form: tx.string for tx in po_tx}
                        po_ent.fuzzy = any(tx.fuzzy for tx in po_tx)
                    if lc_translations and res.entities:
                        last_tx = max(lc_translations, key=lambda tx: tx.date)
                        res.entities[0].last_updated = last_tx.date
                        res.entities[0].last_translator = last_tx.user
                else:
                    for ent in res.translations:
                        ent.strings = {}
                    for tx in lc_translations:
                        key = tx.entity.key
                        if key in res.entities:
                            res.entities[key].strings = {None: tx.string}
                        else:
                            log.warning(f"{lc_scope} No source entry for {key}")
                res.save(locale)
                updated_locales.add(locale)
                for tx in lc_translations:
                    if tx.approved and tx.entity in changed_entities and tx.user:
                        translators[tx.user].add(locale.code)
                count += 1
            except Exception as error:
                log.error(f"{lc_scope} Update failed: {error}")
                continue
    return count, updated_locales, translators
