import logging

from os.path import isfile, join, normpath, relpath

from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths, get_android_locale

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
            locale_map={"android_locale": get_android_locale},
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


def add_newly_configured_files(
    project: Project,
    checkouts: Checkouts,
    paths: L10nConfigPaths | L10nDiscoverPaths,
) -> None:
    if isinstance(paths, L10nDiscoverPaths):
        return
    source, target = checkouts
    src_changed = {join(source.path, co_path) for co_path in source.changed}
    if src_changed.isdisjoint(normpath(cfg_path) for cfg_path in paths.config_paths()):
        return
    tgt_changed = {join(target.path, co_path) for co_path in target.changed}
    current = set(project.resources.current().values_list("path", flat=True))
    for ref_path in paths.ref_paths:
        if (
            relpath(ref_path, paths.ref_root) in current
            or not isfile(ref_path)
            or not is_inside(source.path, ref_path)
        ):
            continue
        if ref_path not in src_changed:
            source.changed.append(relpath(ref_path, source.path))
        tgt_template, locales = paths.target(ref_path)
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
