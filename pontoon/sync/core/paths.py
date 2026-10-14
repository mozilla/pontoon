import logging

from os.path import isfile, join, normpath, relpath
from tomllib import loads
from typing import Any

from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths

from pontoon.base.models import Project
from pontoon.sync.core.checkout import Checkouts, is_inside


log = logging.getLogger(__name__)


class MissingLocaleDirectoryError(IOError):
    """Raised when sync can't find the locale directory."""


def find_paths(
    project: Project, checkouts: Checkouts
) -> L10nConfigPaths | L10nDiscoverPaths:
    src_root = checkouts.source.path

    force_paths = [join(src_root, path) for path in checkouts.source.removed]
    if project.configuration_file:
        paths = L10nConfigPaths(
            join(src_root, project.configuration_file),
            force_paths=force_paths,
        )
        if checkouts.target != checkouts.source:
            paths.base = checkouts.target.path
        name = f"cfg={project.configuration_file}"
    else:
        paths = L10nDiscoverPaths(
            project.checkout_path,
            ref_root=src_root,
            force_paths=force_paths,
            source_locale=["templates", "en-US", "en"],
        )
        if paths.base is None:
            raise MissingLocaleDirectoryError(
                "Base localization directory not found. At least one localized file (which may be empty) is required for automatic path discovery."
            )
        name = "auto"

    rel_root = relpath(paths.ref_root, src_root)
    rel_base = relpath(paths.base, src_root)
    log.debug(f"[{project.slug}] Paths({name}): ref_root={rel_root} base={rel_base}")

    return paths


def find_prev_config_paths(
    project: Project, checkouts: Checkouts, paths: L10nConfigPaths
) -> L10nConfigPaths | None:
    """The project configuration at the last synced revision, if it can be read."""
    source = checkouts.source
    if not source.prev_commit:
        return None

    def load_prev(cfg_path: str) -> dict[str, Any]:
        co_path = relpath(cfg_path, source.path)
        cfg = source.file_at_last_sync(co_path)
        if cfg is None:
            raise FileNotFoundError(co_path)
        return loads(cfg)

    try:
        prev_paths = L10nConfigPaths(
            next(paths.config_paths()),
            cfg_load=load_prev,
        )
    except Exception as error:
        log.warning(f"[{project.slug}] Previous configuration not available: {error}")
        return None
    if checkouts.target != checkouts.source:
        prev_paths.base = checkouts.target.path
    prev_paths.locales = paths.locales
    return prev_paths


def add_newly_configured_files(
    project: Project,
    checkouts: Checkouts,
    paths: L10nConfigPaths,
    config_db_paths_with_renames: set[str],
) -> None:
    source, target = checkouts
    src_changed = {join(source.path, co_path) for co_path in source.changed}
    if src_changed.isdisjoint(normpath(cfg_path) for cfg_path in paths.config_paths()):
        return
    prev_paths = find_prev_config_paths(project, checkouts, paths)
    if prev_paths is None:
        return
    renamed_refs = {join(source.path, new_path) for _, new_path in source.renamed}
    tgt_changed = {join(target.path, co_path) for co_path in target.changed}
    for ref_path in paths.ref_paths:
        if not isfile(ref_path) or not is_inside(source.path, ref_path):
            continue
        is_new = relpath(ref_path, paths.ref_root) not in config_db_paths_with_renames
        tgt_template, locales = paths.target(ref_path)
        if is_new:
            if ref_path not in src_changed:
                source.changed.append(relpath(ref_path, source.path))
        else:
            if ref_path in renamed_refs:
                continue
            prev_tgt_template, _ = prev_paths.target(ref_path)
            if prev_tgt_template == tgt_template:
                continue
        if tgt_template is None:
            continue
        for locale in locales:
            tgt_path = paths.format_target_path(tgt_template, locale)
            if (
                tgt_path not in tgt_changed
                and isfile(tgt_path)
                and is_inside(target.path, tgt_path)
            ):
                target.changed.append(relpath(tgt_path, target.path))
