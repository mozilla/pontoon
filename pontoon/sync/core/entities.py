import logging

from collections import defaultdict
from datetime import datetime
from os.path import exists, isfile, join, relpath, splitext
from typing import Optional

from moz.l10n.model import Entry, Id as L10nId, Message, Resource as L10nResource
from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths
from moz.l10n.resource import parse_resource

from django.db import transaction
from django.db.models import Q

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    Resource,
    Section,
    TranslatedResource,
)
from pontoon.sync.core.checkout import Checkout
from pontoon.sync.formats import as_entity


log = logging.getLogger(__name__)


def sync_resources_from_repo(
    project: Project,
    locale_map: dict[str, Locale],
    checkout: Checkout,
    paths: L10nConfigPaths | L10nDiscoverPaths,
    now: datetime,
) -> tuple[int, set[str], set[str]]:
    """(added_entities_count, changed_source_paths, removed_source_paths"""
    if not checkout.changed and not checkout.removed and not checkout.renamed:
        return 0, set(), set()
    log.info(f"[{project.slug}] Syncing entities from repo...")
    # db_path -> parsed_resource
    updates: dict[str, L10nResource[Message]] = {}
    source_paths = set(paths.ref_paths)
    source_plurals = ["one", "other"]
    for co_path in checkout.changed:
        path = join(checkout.path, co_path)
        if path in source_paths and exists(path):
            db_path = get_db_path(paths, path)
            try:
                updates[db_path] = parse_resource(
                    path, gettext_plurals=source_plurals, gettext_skip_obsolete=True
                )
            except Exception as error:
                log.error(
                    f"[{project.slug}:{db_path}] Skipping resource with parse error: {error}"
                )

    with transaction.atomic():
        renamed_paths = rename_resources(project, paths, checkout)
        removed_paths = remove_resources(project, paths, checkout)
        old_res_added_ent_count, changed_paths = update_resources(project, updates, now)
        new_res_added_ent_count, _ = add_resources(project, updates, changed_paths, now)
        update_translated_resources(project, locale_map, paths)

    return (
        old_res_added_ent_count + new_res_added_ent_count,
        renamed_paths | changed_paths,
        removed_paths,
    )


def rename_resources(
    project: Project, paths: L10nConfigPaths | L10nDiscoverPaths, checkout: Checkout
) -> set[str]:
    if not checkout.renamed:
        return set()
    renamed_db_paths = {
        get_db_path(paths, join(checkout.path, old_path)): get_db_path(
            paths, join(checkout.path, new_path)
        )
        for old_path, new_path in checkout.renamed
    }
    renamed_resources = project.resources.filter(path__in=renamed_db_paths.keys())
    for res in renamed_resources:
        new_db_path = renamed_db_paths[res.path]
        log.info(f"[{project.slug}:{res.path}] Rename as {new_db_path}")
        res.path = new_db_path
    Resource.objects.bulk_update(renamed_resources, ["path"])
    return set(renamed_db_paths.values())


def remove_resources(
    project: Project, paths: L10nConfigPaths | L10nDiscoverPaths, checkout: Checkout
) -> set[str]:
    if not checkout.removed:
        return set()
    removed_resources = project.resources.filter(
        path__in={
            get_db_path(paths, join(checkout.path, co_path))
            for co_path in checkout.removed
        }
    )
    removed_db_paths = {res.path for res in removed_resources}
    if removed_db_paths:
        # FIXME: https://github.com/mozilla/pontoon/issues/2133
        removed_resources.delete()
        rm_count = len(removed_db_paths)
        str_source_files = "source file" if rm_count == 1 else "source files"
        log.info(
            f"[{project.slug}] Removed {rm_count} {str_source_files}: {', '.join(removed_db_paths)}"
        )
    return removed_db_paths


def update_resources(
    project: Project,
    updates: dict[str, L10nResource[Message]],
    now: datetime,
) -> tuple[int, set[str]]:
    changed_resources: dict[int, Resource] | None = (
        {res.pk: res for res in project.resources.filter(path__in=updates.keys())}
        if updates
        else None
    )
    if not changed_resources:
        return 0, set()
    changed_res_paths: set[str] = set(res.path for res in changed_resources.values())
    log.info(f"[{project.slug}] Changed source files: {', '.join(changed_res_paths)}")

    prev_entities: dict[tuple[str, str], Entity] = {
        (changed_resources[e.resource_id].path, e.key or e.string): e
        for e in Entity.objects.filter(
            resource__in=changed_resources, obsolete=False
        ).iterator()
    }
    prev_sections: dict[tuple[str, L10nId, str], Section] = {
        (changed_resources[s.resource_id].path, tuple(s.key), s.comment): s
        for s in Section.objects.filter(resource__in=changed_resources).iterator()
    }

    mod_resources: list[Resource] = []
    new_sections: list[Section] = []
    mod_sections: list[Section] = []
    keep_sections: list[Section] = []
    next_entities: dict[tuple[str, str], Entity] = {}
    for db_res in changed_resources.values():
        l10n_res = updates[db_res.path]
        res_meta = [[m.key, m.value] for m in l10n_res.meta]
        if db_res.meta != res_meta or db_res.comment != l10n_res.comment:
            db_res.meta = res_meta
            db_res.comment = l10n_res.comment
            mod_resources.append(db_res)
        idx = 0
        for l10n_section in l10n_res.sections:
            section_key = (db_res.path, l10n_section.id, l10n_section.comment)
            section_meta = [[m.key, m.value] for m in l10n_section.meta]
            db_section = prev_sections.get(section_key, None)
            if db_section is None:
                db_section = Section(
                    resource=db_res,
                    key=l10n_section.id,
                    meta=section_meta,
                    comment=l10n_section.comment,
                )
                new_sections.append(db_section)
            elif db_section.meta != section_meta:
                db_section.meta = section_meta
                mod_sections.append(db_section)
            has_entries = False
            for entry in l10n_section.entries:
                if isinstance(entry, Entry):
                    entity = as_entity(l10n_res.format, l10n_section.id, entry, now)
                    entity.order = idx
                    entity.resource = db_res
                    entity.section = db_section
                    next_entities[db_res.path, entity.key or entity.string] = entity
                    idx += 1
                    has_entries = True
            if has_entries:
                if db_section.pk:
                    keep_sections.append(db_section)
            elif not db_section.pk:
                new_sections.pop()

    obsolete_entities: list[Entity] = []
    log_rm: dict[str, list[str]] = defaultdict(list)
    for key, prev_ent in prev_entities.items():
        if key not in next_entities:
            prev_ent.obsolete = True
            prev_ent.date_obsoleted = now
            prev_ent.section = None
            obsolete_entities.append(prev_ent)
            key_path, key_entity = key
            log_rm[key_path].append(key_entity)
    Entity.objects.bulk_update(
        obsolete_entities, ["obsolete", "date_obsoleted", "section"]
    )

    Resource.objects.bulk_update(mod_resources, ["meta", "comment"])

    # Order matters here: Sections can be simultaneously modified and deleted.
    Section.objects.bulk_update(mod_sections, ["meta"])
    del_section_ids = [
        section.pk for section in prev_sections.values() if section not in keep_sections
    ]
    if del_section_ids:
        Section.objects.filter(pk__in=del_section_ids).delete()

    # The Section.pk values need to be set before we modify or create Entities.
    Section.objects.bulk_create(new_sections)

    mod_fields = [
        "string",
        "comment",
        "meta",
        "source",
        "context",
    ]
    mod_entities: list[Entity] = []
    added_entities: list[Entity] = []
    log_mod: dict[str, list[str]] = defaultdict(list)
    log_add: dict[str, list[str]] = defaultdict(list)
    for key, next_ent in next_entities.items():
        key_path, key_entity = key
        if key in prev_entities:
            mod_ent = entity_update(prev_entities[key], next_ent, mod_fields)
            if mod_ent is not None:
                mod_entities.append(mod_ent)
                log_mod[key_path].append(key_entity)
        else:
            added_entities.append(next_ent)
            log_add[key_path].append(key_entity)
    Entity.objects.bulk_update(mod_entities, mod_fields)

    # FIXME: Entity order should be updated on insertion
    # https://github.com/mozilla/pontoon/issues/2115
    added_entities = Entity.objects.bulk_create(added_entities)
    add_count = len(added_entities)

    if log_rm or log_add or log_mod:
        for path in sorted(list(log_rm.keys() | log_add.keys() | log_mod.keys())):
            for desc, log_data in (
                ("Obsolete", log_rm),
                ("Changed", log_mod),
                ("New", log_add),
            ):
                ls = log_data.get(path, None)
                if ls:
                    scope = f"[{project.slug}:{path}]"
                    names = ", ".join(ls).replace("\n", "¶")
                    log.info(f"{scope} {desc} entities ({len(ls)}): {names}")
    return add_count, changed_res_paths


def add_resources(
    project: Project,
    updates: dict[str, L10nResource[Message]],
    changed_paths: set[str],
    now: datetime,
) -> tuple[int, set[str]]:
    new_resources = [
        Resource(project=project, path=db_path, format=get_path_format(db_path))
        for db_path, res in updates.items()
        if next(res.all_entries(), None) and db_path not in changed_paths
    ]
    if not new_resources:
        return 0, set()

    Resource.objects.bulk_create(new_resources)
    ordered_resources = project.resources.order_by("path")
    for idx, r in enumerate(ordered_resources):
        r.order = idx
    Resource.objects.bulk_update(ordered_resources, ["order"])

    new_sections: list[Section] = []
    new_entities: list[Entity] = []
    for db_res in new_resources:
        l10n_res = updates[db_res.path]
        idx = 0
        for l10n_section in l10n_res.sections:
            db_section = Section(
                resource=db_res,
                key=l10n_section.id,
                meta=[[m.key, m.value] for m in l10n_section.meta],
                comment=l10n_section.comment,
            )
            has_entries = False
            for entry in l10n_section.entries:
                if isinstance(entry, Entry):
                    entity = as_entity(l10n_res.format, l10n_section.id, entry, now)
                    entity.order = idx
                    entity.resource = db_res
                    entity.section = db_section
                    new_entities.append(entity)
                    idx += 1
                    has_entries = True
            if has_entries:
                new_sections.append(db_section)
    Section.objects.bulk_create(new_sections)
    Entity.objects.bulk_create(new_entities)

    ent_count = len(new_entities)
    added_paths = {ar.path for ar in new_resources}
    log.info(
        f"[{project.slug}] New source files with {ent_count} entities: {', '.join(added_paths)}"
    )
    return ent_count, added_paths


def update_translated_resources(
    project: Project,
    locale_map: dict[str, Locale],
    paths: L10nConfigPaths | L10nDiscoverPaths,
) -> None:
    prev_tr_keys: set[tuple[int, int]] = set(
        (tr["resource_id"], tr["locale_id"])
        for tr in TranslatedResource.objects.filter(resource__project=project)
        .values("resource_id", "locale_id")
        .iterator()
    )
    add_tr: list[TranslatedResource] = []
    for resource in Resource.objects.filter(project=project).iterator():
        _, locales = paths.target(resource.path)
        for lc in locales:
            locale = locale_map.get(lc, None)
            if is_translated_resource(paths, resource, locale):
                assert locale is not None
                key = (resource.pk, locale.pk)
                if key in prev_tr_keys:
                    prev_tr_keys.remove(key)
                else:
                    add_tr.append(TranslatedResource(resource=resource, locale=locale))
    if add_tr:
        add_tr = TranslatedResource.objects.bulk_create(add_tr)
        add_by_res: dict[str, list[str]] = defaultdict(list)
        for tr in add_tr:
            add_by_res[tr.resource.path].append(tr.locale.code)
        for res_path, locale_codes in add_by_res.items():
            locale_codes.sort()
            log.info(
                f"[{project.slug}:{res_path}] Added for translation in: {', '.join(locale_codes)}"
            )
    if prev_tr_keys:
        del_tr_q = Q()
        for resource_id, locale_id in prev_tr_keys:
            del_tr_q |= Q(resource_id=resource_id, locale_id=locale_id)
        _, del_dict = TranslatedResource.objects.filter(del_tr_q).delete()
        del_count = del_dict.get("base.translatedresource", 0)
        str_tr = "translated resource" if del_count == 1 else "translated resources"
        log.info(f"[{project.slug}] Removed {del_count} {str_tr}")


def is_translated_resource(
    paths: L10nConfigPaths | L10nDiscoverPaths,
    resource: Resource,
    locale: Locale | None,
) -> bool:
    if locale is None:
        return False

    if resource.format == "po":
        # For gettext, only create TranslatedResource
        # if the resource exists for the locale.
        target, _ = paths.target(resource.path)
        if target is None:
            return False
        target_path = paths.format_target_path(target, locale.code)
        return isfile(target_path)
    return True


def entity_update(
    current: Entity, update_from: Entity, fields: list[str]
) -> Optional[Entity]:
    updated = False
    for field in fields:
        value = getattr(update_from, field)
        if getattr(current, field) != value:
            setattr(current, field, value)
            updated = True
    return current if updated else None


def get_db_path(paths: L10nConfigPaths | L10nDiscoverPaths, file_path: str) -> str:
    rel_path = relpath(file_path, paths.ref_root)
    return (
        rel_path[:-1]
        if isinstance(paths, L10nDiscoverPaths) and rel_path.endswith(".pot")
        else rel_path
    )


def get_path_format(path: str) -> str:
    _, extension = splitext(path)
    path_format = extension[1:].lower()

    # Special case: pot files are considered the po format
    if path_format == "pot":
        return "po"
    elif path_format == "xlf":
        return "xliff"
    else:
        return path_format
