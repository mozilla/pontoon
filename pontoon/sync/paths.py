import logging

from os.path import join

from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths, get_android_locale

from pontoon.base.models import Project
from pontoon.sync.checkouts import Checkouts


log = logging.getLogger(__name__)


class MissingLocaleDirectoryError(IOError):
    """Raised when sync can't find the locale directory."""


def get_paths(
    project: Project, checkouts: Checkouts
) -> L10nConfigPaths | L10nDiscoverPaths:
    force_paths = [
        join(checkouts.source.path, path) for path in checkouts.source.removed
    ]
    if project.configuration_file:
        paths = L10nConfigPaths(
            join(checkouts.source.path, project.configuration_file),
            locale_map={"android_locale": get_android_locale},
            force_paths=force_paths,
        )
        if checkouts.target != checkouts.source:
            paths.base = checkouts.target.repo.checkout_path
        return paths
    else:
        paths = L10nDiscoverPaths(
            project.checkout_path,
            ref_root=checkouts.source.path,
            force_paths=force_paths,
            source_locale=["templates", "en-US", "en"],
        )
        if paths.base is None:
            raise MissingLocaleDirectoryError("Base localization directory not found")
        return paths


class UploadPaths:
    """
    moz.l10n.paths -like interface for sync'ing content from a single file.
    Implements minimal functionality required by `find_db_updates()`.
    """

    ref_root = ""

    def __init__(self, ref_path: str, locale_code: str, file_path: str):
        self._ref_path = ref_path
        self._locale_code = locale_code
        self._file_path = file_path

    def find_reference(self, target_path: str):
        return (
            (self._ref_path, {"locale": self._locale_code})
            if target_path == self._file_path
            else None
        )
