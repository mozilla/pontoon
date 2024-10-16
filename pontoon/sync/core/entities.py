import logging

from datetime import datetime
from os.path import exists, isfile, join, relpath, splitext

from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths

from django.db import transaction

from pontoon.base.models import Entity, Locale, Project, Resource, TranslatedResource
from pontoon.base.models.entity import get_word_count
from pontoon.sync.core.checkout import Checkout
from pontoon.sync.formats import parse
from pontoon.sync.formats.exceptions import ParseError
from pontoon.sync.formats.silme import SilmeEntity, SilmeResource  # Approximate types


log = logging.getLogger(__name__)

BILINGUAL_FORMATS = {"po", "xliff"}


def sync_entities_from_repo(
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
    updates: dict[str, SilmeResource | None] = {}
    source_paths = set(paths.ref_paths)
    source_locale = Locale.objects.get(code="en-US")
    for co_path in checkout.changed:
        path = join(checkout.path, co_path)
        if path in source_paths and exists(path):
            db_path = get_db_path(paths, path)
            try:
                res = parse(path, locale=source_locale)
            except ParseError as error:
                log.error(
                    f"[{project.slug}:{db_path}] Skipping resource with parse error: {error}"
                )
                res = None
            except ValueError as error:
                if str(error).startswith("Translation format"):
                    log.warning(
                        f"[{project.slug}:{db_path}] Skipping resource with unsupported format"
                    )
                    res = None
                else:
                    raise error
            updates[db_path] = res

    with transaction.atomic():
        renamed_paths = rename_resources(project, paths, checkout)
        removed_paths = remove_resources(project, paths, checkout)
        old_res_added_ent_count, changed_paths = update_resources(project, updates, now)
        new_res_added_ent_count, _ = add_resources(
            project, locale_map, paths, updates, changed_paths, now
        )

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
    removed_db_paths = {
        get_db_path(paths, join(checkout.path, co_path)) for co_path in checkout.removed
    }
    # FIXME: https://github.com/mozilla/pontoon/issues/2133
    rm_count, _ = project.resources.filter(path__in=removed_db_paths).delete()
    if rm_count:
        str_source_files = "source file" if rm_count == 1 else "source files"
        log.info(
            f"[{project.slug}] Removed {rm_count} {str_source_files}: {', '.join(removed_db_paths)}"
        )
        return removed_db_paths
    else:
        return set()


def update_resources(
    project: Project,
    updates: dict[str, SilmeResource | None],
    now: datetime,
) -> tuple[int, set[str]]:
    changed_resources = (
        project.resources.filter(path__in=updates.keys()) if updates else None
    )
    if not changed_resources:
        return 0, set()

    prev_entities = {
        (e.resource.path, e.key or e.string): e
        for e in Entity.objects.filter(resource__in=changed_resources, obsolete=False)
        .select_related("resource")
        .iterator()
    }
    next_entities = {
        (path, entity.key or entity.string): entity
        for path, entity in (
            (cr.path, entity_from_source(cr, now, 0, tx))
            for cr in changed_resources
            for tx in updates[cr.path].translations
        )
    }

    obsolete_entities = [
        ent
        for key, ent in prev_entities.items()
        if key in prev_entities.keys() - next_entities.keys()
    ]
    for ent in obsolete_entities:
        ent.obsolete = True
        ent.date_obsoleted = now
    obs_count = Entity.objects.bulk_update(
        obsolete_entities, ["obsolete", "date_obsoleted"]
    )

    mod_count = Entity.objects.bulk_update(
        (
            ent
            for key, ent in next_entities.items()
            if key in prev_entities.keys() & next_entities.keys()
            and not entities_same(ent, prev_entities[key])
        ),
        [
            "string",
            "string_plural",
            "comment",
            "source",
            "group_comment",
            "resource_comment",
            "context",
        ],
    )

    # FIXME: Entity order should be updated on insertion
    # https://github.com/mozilla/pontoon/issues/2115
    added_entities = Entity.objects.bulk_create(
        ent
        for key, ent in next_entities.items()
        if key in next_entities.keys() - prev_entities.keys()
    )
    add_count = len(added_entities)

    delta = [
        f"added {add_count}" if add_count else "",
        f"changed {mod_count}" if mod_count else "",
        f"obsoleted {obs_count}" if obs_count else "",
    ]
    if any(delta):
        ds = ", ".join(d for d in delta if d)
        log.info(f"[{project.slug}] Source entity updates: {ds}")
    return add_count, set(changed_resources.values_list("path", flat=True))


def add_resources(
    project: Project,
    locale_map: dict[str, Locale],
    paths: L10nConfigPaths | L10nDiscoverPaths,
    updates: dict[str, SilmeResource | None],
    changed_paths: set[str],
    now: datetime,
) -> tuple[int, set[str]]:
    added_resources = [
        Resource(project=project, path=db_path, format=get_path_format(db_path))
        for db_path, res in updates.items()
        if res is not None and db_path not in changed_paths
    ]
    if not added_resources:
        return 0, set()

    added_resources = Resource.objects.bulk_create(added_resources)
    ordered_resources = project.resources.order_by("path")
    for idx, r in enumerate(ordered_resources):
        r.order = idx
    Resource.objects.bulk_update(ordered_resources, ["order"])

    added_entities = Entity.objects.bulk_create(
        (
            entity_from_source(resource, now, idx, tx)
            for resource in added_resources
            for idx, tx in enumerate(updates[resource.path].translations)
        )
    )

    def is_translated_resource(resource: Resource, locale_code: str) -> bool:
        if locale_code not in locale_map:
            return False
        if resource.format in BILINGUAL_FORMATS:
            # For bilingual formats, only create TranslatedResource
            # if the resource exists for the locale.
            target = paths.target(resource.path)  # , locale_code)
            if target is None:
                return False
            target_path = paths.format_target_path(target[0], locale_code)
            return isfile(target_path)
        return True

    TranslatedResource.objects.bulk_create(
        TranslatedResource(resource=resource, locale=locale_map[locale_code])
        for resource in added_resources
        for locale_code in paths.target(resource.path)[1]
        if is_translated_resource(resource, locale_code)
    )

    ent_count = len(added_entities)
    added_paths = {ar.path for ar in added_resources}
    log.info(
        f"[{project.slug}] New source files with {ent_count} entities: {', '.join(added_paths)}"
    )
    return ent_count, added_paths


def entity_from_source(
    resource: Resource, now: datetime, idx: int, tx: SilmeEntity
) -> Entity:
    comments = getattr(tx, "comments", None)
    group_comments = getattr(tx, "group_comments", None)
    resource_comments = getattr(tx, "resource_comments", None)
    return Entity(
        string=tx.source_string,
        string_plural=tx.source_string_plural,
        key=tx.key,
        comment="\n".join(comments) if comments else "",
        order=tx.order or idx,
        source=tx.source,
        resource=resource,
        date_created=now,
        group_comment="\n".join(group_comments) if group_comments else "",
        resource_comment="\n".join(resource_comments) if resource_comments else "",
        context=tx.context,
        word_count=get_word_count(tx.source_string),
    )


def entities_same(a: Entity, b: Entity) -> bool:
    return (
        a.string == b.string
        and a.string_plural == b.string_plural
        and a.comment == b.comment
        and a.source == b.source
        and a.group_comment == b.group_comment
        and a.resource_comment == b.resource_comment
        and a.context == b.context
    )


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
