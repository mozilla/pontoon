import html
import logging

from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from os import makedirs, remove
from os.path import commonpath, dirname, isfile

from moz.l10n.formats import Format
from moz.l10n.formats.xliff import xliff_is_xcode
from moz.l10n.message import message_from_json, serialize_message
from moz.l10n.model import (
    CatchallKey,
    Entry,
    Id,
    Message,
    Metadata,
    PatternMessage,
    Resource,
    Section,
    SelectMessage,
)
from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths
from moz.l10n.resource import serialize_resource

from django.conf import settings
from django.db.models import Q
from django.db.models.query import QuerySet

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    Resource as DbResource,
    Translation,
    User,
)
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
            tr_name = translator.display_name
            tr_email = translator.email
            lc_str = ", ".join(sorted(lc_set))
            commit_msg += f"\nCo-authored-by: {tr_name} ({lc_str}) <{tr_email}>"

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
    # db_path -> (db_res, {Locale})
    # Where an empty set stands for "all locales"
    changed_resources: dict[str, tuple[DbResource, set[Locale]]] = {
        db_res.path: (db_res, set())
        for db_res in DbResource.objects.filter(
            project=project, path__in=changed_source_paths
        )
    }
    for change in db_changes:
        if change.locale in readonly_locales:
            continue
        db_res = change.entity.resource
        if db_res.path not in changed_resources:
            changed_resources[db_res.path] = (db_res, {change.locale})
        else:
            prev = changed_resources[db_res.path]
            if prev[1]:
                prev[1].add(change.locale)
    changed_entities = {change.entity for change in db_changes}
    if changed_resources:
        n = len(changed_resources)
        str_resources = "resource" if n == 1 else "resources"
        log.info(f"[{project.slug}] Updating {n} changed {str_resources}")

    updated_locales: set[Locale] = set()
    translators: dict[User, set[str]] = defaultdict(set)
    for path, (db_res, locales_) in changed_resources.items():
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
        res = build_moz_l10n_resource(db_res)
        for locale in locales:
            lc_translations = {
                tuple(tx.entity.key): tx
                for tx in translations
                if tx.locale_id == locale.pk
            }
            target_path = paths.format_target_path(target, locale.code)
            if not lc_translations and not isfile(target_path):
                continue
            try:
                lc_plurals = locale.cldr_plurals_list()
                tr_res = build_translated_resource(locale, lc_translations, res)
                makedirs(dirname(target_path), exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as file:
                    for line in serialize_resource(tr_res, gettext_plurals=lc_plurals):
                        file.write(line)
                updated_locales.add(locale)
                for tx in lc_translations.values():
                    if tx.approved and tx.entity in changed_entities and tx.user:
                        translators[tx.user].add(locale.code)
                count += 1
            except Exception as error:
                log.error(
                    f"[{project.slug}:{path}, {locale.code}] Update failed: {error}"
                )
                continue
    return count, updated_locales, translators


def build_moz_l10n_resource(db_res: DbResource) -> Resource:
    if db_res.format == DbResource.Format.XCODE:
        format = Format.xliff
    else:
        try:
            format = Format[db_res.format]
        except KeyError:
            raise ValueError(f"Unsupported format: {db_res.format}")
    db_sections = {s.pk: s for s in db_res.sections.iterator()}
    sections: list[Section[Message]] = []
    prev_s_pk = -1
    for e in db_res.entities.filter(obsolete=False).order_by("order").iterator():
        entry = _entry_from_entity(format, e)
        s_pk = e.section_id
        assert s_pk is not None
        if s_pk == prev_s_pk:
            sections[-1].entries.append(entry)
            continue

        # Comment-based sections (as in Fluent) can be non-contiguous,
        # and should remain that way.
        # Sections with a non-empty key should stay together,
        # even if the Entity.order values are not in the right order.
        db_section = db_sections[s_pk]
        prev_s_pk = s_pk
        s_id = tuple(db_section.key)
        if s_id:
            section = next((s for s in sections if s.id == s_id), None)
            if section is not None:
                section.entries.append(entry)
                continue

        section = Section(
            id=s_id,
            comment=db_section.comment,
            meta=[Metadata(k, v) for k, v in db_section.meta],
            entries=[entry],
        )
        sections.append(section)
    return Resource(
        format=format,
        comment=db_res.comment,
        meta=[Metadata(k, v) for k, v in db_res.meta],
        sections=sections,
    )


def _entry_from_entity(format: Format, e: Entity) -> Entry[Message]:
    key = e.key[1:] if format in {Format.ini, Format.xliff} else e.key
    entry = Entry(
        id=tuple(key),
        comment=e.comment,
        meta=[Metadata(k, v) for k, v in e.meta],
        value=message_from_json(e.value),
        properties={k: message_from_json(v) for k, v in e.properties.items()}
        if e.properties
        else {},
    )
    if format == Format.xliff:
        source = serialize_message(Format.xliff, entry.value)
        entry.set_meta("source", html.unescape(source))
    return entry


def build_translated_resource(
    locale: Locale, translations: dict[Id, Translation], res: Resource[Message]
) -> Resource[Message]:
    res = deepcopy(res)
    for section in res.sections:
        rm = []
        for entry in section.entries:
            assert isinstance(entry, Entry)
            tx = translations.get(section.id + entry.id, None)
            if tx is not None:
                _set_translation(res.format, entry, tx)
            else:
                match res.format:
                    case Format.gettext if isinstance(entry.value, SelectMessage):
                        entry.value.variants = {(CatchallKey(),): []}
                    case Format.gettext | Format.xliff:
                        entry.value = PatternMessage([])
                    case _:
                        rm.append(entry)
        if rm:
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
            lc = str(locale.code)
            if xliff_is_xcode(res):
                lc = ios_locale_map.get(lc, lc)
            for section in res.sections:
                if section.get_meta("@source-language") is not None:
                    section.set_meta("@target-language", lc)

        case _:
            res.sections = [
                section
                for section in res.sections
                if any(isinstance(entry, Entry) for entry in section.entries)
            ]
    return res


def _set_translation(format: Format | None, entry: Entry, tx: Translation) -> None:
    match format:
        case Format.fluent:
            entry.value = message_from_json(tx.value)
            is_term = entry.id[0].startswith("-")
            entry.properties = (
                {
                    name: message_from_json(pv)
                    for name, pv in tx.properties.items()
                    if is_term or name in entry.properties
                }
                if tx.properties
                else {}
            )
        case Format.android | Format.gettext | Format.webext | Format.xliff:
            msg = message_from_json(tx.value)
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

        case _:
            entry.value = message_from_json(tx.value)
