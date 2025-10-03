import logging

from collections import defaultdict
from datetime import datetime
from os import makedirs, remove
from os.path import commonpath, dirname, isfile, join, normpath
from re import compile

from moz.l10n.formats import Format
from moz.l10n.message import parse_message
from moz.l10n.model import (
    CatchallKey,
    Entry,
    Expression,
    Id,
    Metadata,
    PatternMessage,
    Resource,
    Section,
    SelectMessage,
    VariableRef,
)
from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths
from moz.l10n.resource import parse_resource, serialize_resource

from django.conf import settings
from django.db.models import Q
from django.db.models.query import QuerySet

from pontoon.base.models import Locale, Project, Translation, User
from pontoon.base.models.changed_entity_locale import ChangedEntityLocale
from pontoon.sync.core.checkout import Checkouts
from pontoon.sync.repositories import CommitToRepositoryException, get_repo


log = logging.getLogger(__name__)

# Retaining these in the .po files is unnecessary & misleading,
# and changes to POT-Creation-Date cause unnecessary churn.
# Pontoon itself is the appropriate reference.
gettext_trim_headers = (
    "Language-Team",
    "Last-Translator",
    "PO-Revision-Date",
    "POT-Creation-Date",
    "Report-Msgid-Bugs-To",
    "X-Generator",
)

# Hacky solution for https://github.com/mozilla-mobile/firefox-ios/issues/9632
# from https://github.com/mozilla-l10n/firefoxios-l10n/blob/d60eef5ae23fde3f5bcd6d8e5290aab5fd5cc282/.github/scripts/update_other_locales.py#L130-L139
# TODO: This should almost certainly be handled better
ios_locale_map = {
    "ga-IE": "ga",
    "nb-NO": "nb",
    "nn-NO": "nn",
    "sat": "sat-Olck",
    "sv-SE": "sv",
    "tl": "fil",
    "zgh": "tzm",
}


def sync_translations_to_repo(
    project: Project,
    commit: bool,
    locale_map: dict[str, Locale],
    checkouts: Checkouts,
    paths: L10nConfigPaths | L10nDiscoverPaths,
    db_changes: QuerySet[ChangedEntityLocale],
    changed_source_paths: set[str],
    removed_source_paths: set[str],
    now: datetime,
) -> bool:
    """Returns `True` if the sync includes changes to the repo."""
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
        return False

    if not commit:
        log.info(f"[{project.slug}] Skipping commit & push")
        return True

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

    return True


def delete_removed_resources(
    project: Project,
    paths: L10nConfigPaths | L10nDiscoverPaths,
    locale_map: dict[str, Locale],
    readonly_locales: QuerySet[Locale],
    removed_source_paths: set[str],
) -> int:
    count = 0
    for path in removed_source_paths:
        log_scope = f"[{project.slug}:{path}]"
        log.info(f"{log_scope} Removing for all locales")
        target, locale_codes = paths.target(path)
        if target and paths.base and commonpath((paths.base, target)) == paths.base:
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
    readonly_locales: list[Locale] | QuerySet[Locale],
    db_changes: QuerySet[ChangedEntityLocale],
    changed_source_paths: set[str],
    now: datetime,
) -> tuple[int, set[Locale], dict[User, set[str]]]:
    count = 0
    # db_path -> {Locale}, empty set stands for "all locales"
    changed_resources: dict[str, set[Locale]] = {
        path: set() for path in changed_source_paths
    }
    for change in db_changes:
        if change.locale in readonly_locales:
            continue
        path = str(change.entity.resource.path)
        if path not in changed_resources:
            changed_resources[path] = {change.locale}
        else:
            prev = changed_resources[path]
            if prev:
                prev.add(change.locale)
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
        if commonpath((paths.base or "", target)) != paths.base:
            log.error(f"{log_scope} Invalid resource path")
            continue
        locales = locales_ or {
            locale
            for locale in (
                locale_map[lc] for lc in sorted(locale_codes) if lc in locale_map
            )
            if locale not in readonly_locales
        }
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
                active=True,
            )
            .filter(
                Q(approved=True)
                | Q(pretranslated=True, warnings__isnull=True)
                | Q(fuzzy=True)
            )
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
                lc_plurals = locale.cldr_plurals_list()
                res = parse_resource(ref_path)
                set_translations(locale, lc_translations, res)
                makedirs(dirname(target_path), exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as file:
                    for line in serialize_resource(res, gettext_plurals=lc_plurals):
                        file.write(line)
                updated_locales.add(locale)
                for tx in lc_translations:
                    if tx.approved and tx.entity in changed_entities and tx.user:
                        translators[tx.user].add(locale.code)
                count += 1
            except Exception as error:
                log.error(f"{lc_scope} Update failed: {error}")
                continue
    return count, updated_locales, translators


def set_translations(
    locale: Locale, translations: list[Translation], res: Resource
) -> None:
    if res.format == Format.fluent:
        trans_res = parse_resource(
            Format.fluent, "".join(tx.string for tx in translations)
        )
        trans_entries: dict[Id, Entry | None] = {
            entry.id: entry
            for section in trans_res.sections
            for entry in section.entries
            if isinstance(entry, Entry)
        }
        for section in res.sections:
            rm: list[Entry] = []
            for entry in section.entries:
                if isinstance(entry, Entry):
                    te = trans_entries.get(entry.id, None)
                    if te is None:
                        rm.append(entry)
                    else:
                        entry.value = te.value
                        entry.properties = (
                            te.properties
                            if entry.id[0].startswith("-")
                            else {
                                name: tp
                                for name, tp in te.properties.items()
                                if name in entry.properties
                            }
                        )
            if rm:
                section.entries = [e for e in section.entries if e not in rm]
    else:
        for section in res.sections:
            if (
                res.format == Format.xliff
                and section.get_meta("@source-language") is not None
            ):
                prev_tgt = next(
                    (m for m in section.meta if m.key == "@target-language"), None
                )
                lc = ios_locale_map.get(locale.code, locale.code)
                if prev_tgt is None:
                    res.meta.append(Metadata("@target-language", lc))
                else:
                    prev_tgt.value = lc

            rm: list[Entry] = []
            for entry in section.entries:
                if isinstance(entry, Entry):
                    if not set_translation(translations, res.format, section, entry):
                        rm.append(entry)
            if rm and res.format not in (Format.gettext, Format.xliff):
                section.entries = [e for e in section.entries if e not in rm]

    match res.format:
        case Format.gettext:
            header = {m.key: m.value for m in res.meta}
            header["Language"] = locale.code.replace("-", "_")
            header["Plural-Forms"] = (
                f"nplurals={locale.nplurals or '1'}; plural={locale.plural_rule or '0'};"
            )
            header["Generated-By"] = "Pontoon"
            res.meta = [
                Metadata(key, value)
                for key, value in header.items()
                if key not in gettext_trim_headers
            ]
        case Format.xliff:
            pass
        case _:
            res.sections = [
                section
                for section in res.sections
                if any(isinstance(entry, Entry) for entry in section.entries)
            ]


webext_placeholder = compile(r"\$([a-zA-Z0-9_@]+)\$|(\$[1-9])|\$(\$+)")


def set_translation(
    translations: list[Translation],
    format: Format | None,
    section: Section,
    entry: Entry,
) -> bool:
    key = list(section.id + entry.id)
    tx = next((tx for tx in translations if tx.entity.key == key), None)
    if tx is None:
        if format == Format.gettext:
            if isinstance(entry.value, SelectMessage):
                entry.value.variants = {(CatchallKey(),): []}
            else:
                entry.value = PatternMessage([])
            return True
        else:
            return False

    match format:
        case Format.android | Format.gettext:
            msg = parse_message(Format.mf2, tx.string)
            if isinstance(entry.value, SelectMessage):
                entry.value.variants = (
                    {(CatchallKey(),): msg.pattern}
                    if isinstance(msg, PatternMessage)
                    else msg.variants
                )
            else:
                assert isinstance(entry.value, PatternMessage)
                assert isinstance(msg, PatternMessage)
                entry.value = msg
            if format == Format.gettext:
                fuzzy_flag = Metadata("flag", "fuzzy")
                if tx.fuzzy:
                    if fuzzy_flag not in entry.meta:
                        entry.meta.insert(0, fuzzy_flag)
                elif fuzzy_flag in entry.meta:
                    entry.meta = [m for m in entry.meta if m != fuzzy_flag]

        case Format.webext if (
            isinstance(entry.value, PatternMessage) and entry.value.declarations
        ):
            # With a message value, placeholders in string parts would have their
            # $ characters doubled to escape them.
            entry.value.pattern = []
            pos = 0
            for m in webext_placeholder.finditer(tx.string):
                start = m.start()
                if start > pos:
                    entry.value.pattern.append(tx.string[pos:start])
                if m[1]:
                    ph_name = m[1].replace("@", "_")
                    if ph_name[0].isdigit():
                        ph_name = f"_{ph_name}"
                    ph_name = next(
                        (
                            name
                            for name in entry.value.declarations
                            if name.lower() == ph_name.lower()
                        ),
                        ph_name,
                    )
                    pass
                else:
                    ph_name = m[0]
                entry.value.pattern.append(
                    Expression(VariableRef(ph_name), attributes={"source": m[0]})
                )
                pos = m.end()
            if pos < len(tx.string):
                entry.value.pattern.append(tx.string[pos:])

        case _:
            entry.value = tx.string

    return True
