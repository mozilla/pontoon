import logging
from os.path import join

from moz.l10n.paths import L10nConfigPaths, L10nDiscoverPaths, get_android_locale

from pontoon.base.models import Project
from pontoon.sync.checkouts import Checkouts
from pontoon.sync.vcs.project import MissingLocaleDirectoryError

log = logging.getLogger(__name__)


def get_paths(
    project: Project, checkouts: Checkouts
) -> L10nConfigPaths | L10nDiscoverPaths:
    if project.configuration_file:
        paths = L10nConfigPaths(
            join(checkouts.source.path, project.configuration_file),
            locale_map={"android_locale": get_android_locale},
        )
        if checkouts.target != checkouts.source:
            paths.base = checkouts.target.repo.checkout_path
        return paths
    else:
        paths = L10nDiscoverPaths(project.checkout_path, checkouts.source.path)
        if paths.base is None:
            raise MissingLocaleDirectoryError("Base localization directory not found")
        return paths
