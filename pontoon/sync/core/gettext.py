from collections import defaultdict
from os import scandir
from os.path import dirname, isdir

from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths

from pontoon.base.models import Locale, Project


def find_empty_gettext_locales(
    project: Project,
    locale_map: dict[str, Locale],
    paths: L10nConfigPaths | L10nDiscoverPaths,
) -> set[str]:
    # Locales with empty gettext target folders (no .po files).
    # These locales get bootstrapped from the .pot templates, while locales
    # that already have even a partial subset of .po files are left unchanged.
    locale_folders: dict[str, set[str]] = defaultdict(set)
    gettext_paths = project.resources.filter(
        format="gettext", obsolete=False
    ).values_list("path", flat=True)
    for path in gettext_paths:
        target, locale_codes = paths.target(path)
        if target is None:
            continue
        for lc in locale_codes:
            if lc in locale_map:
                locale_folders[lc].add(dirname(paths.format_target_path(target, lc)))

    return {
        lc
        for lc, folders in locale_folders.items()
        if not any(_folder_has_po(f) for f in folders)
    }


def _folder_has_po(folder: str) -> bool:
    if not isdir(folder):
        return False
    with scandir(folder) as it:
        return any(entry.is_file() and entry.name.endswith(".po") for entry in it)
