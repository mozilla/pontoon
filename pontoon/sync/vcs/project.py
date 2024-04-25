import logging
import os
import shutil
from itertools import chain

from django.utils.functional import cached_property

from pontoon.base import MOZILLA_REPOS
from pontoon.sync.exceptions import ParseError
from pontoon.sync.repositories import get_changed_files
from pontoon.sync.utils import (
    directory_contains_resources,
    get_parent_directory,
    is_asymmetric_resource,
    is_hidden,
    is_resource,
    locale_directory_path,
    source_to_locale_path,
    uses_undercore_as_separator,
)
from pontoon.sync.vcs.config import VCSConfiguration
from pontoon.sync.vcs.resource import VCSResource

log = logging.getLogger(__name__)


class MissingSourceRepository(Exception):
    """
    Raised when project can't find the repository
    which contains source files.
    """


class MissingSourceDirectoryError(Exception):
    """Raised when sync can't find the source directory for the locales."""


class MissingLocaleDirectoryError(IOError):
    """Raised when sync can't find the locale directory."""


class VCSProject:
    """
    Container for project data that is stored on the filesystem and
    pulled from a remote VCS.
    """

    SOURCE_DIR_SCORES = {
        "templates": 3,
        "en-US": 2,
        "en-us": 2,
        "en_US": 2,
        "en_us": 2,
        "en": 1,
    }
    SOURCE_DIR_NAMES = SOURCE_DIR_SCORES.keys()

    def __init__(
        self,
        db_project,
        now=None,
        locales=None,
        repo_locales=None,
        added_paths=None,
        changed_paths=None,
        force=False,
    ):
        """
        Load resource paths from the given db_project and parse them
        for translation data.

        :param Project db_project:
            Project model instance for the project we're going to be
            reading files for.
        :param datetime.datetime now:
            Sync start time.
        :param list locales:
            List of Locale model instances for the locales that we want
            to parse. Defaults to parsing resources for all enabled
            locales on the project.
        :param dict repo_locales:
            A dict of repository PKs and their currently checked out locales
            (not neccessarily matching the ones stored in the DB).
        :param list added_paths:
            List of added source file paths
        :param list changed_paths:
            List of changed source file paths
        :param bool force:
            Scans all resources in repository
        :param VCSConfiguration configuration:
            Project configuration, provided by the optional configuration file.
        """
        self.db_project = db_project
        self.now = now
        self.locales = locales if locales is not None else db_project.locales.all()
        self.repo_locales = repo_locales
        self.added_paths = added_paths or []
        self.changed_paths = changed_paths or []
        self.force = force
        self.synced_locales = set()

        self.configuration = None
        if db_project.configuration_file:
            self.configuration = VCSConfiguration(self)

    @cached_property
    def changed_files(self):
        if self.force or (
            self.db_project.configuration_file and self.changed_config_files
        ):
            # All files are marked as changed
            return None

        if self.locales:
            return self.changed_locales_files
        else:
            return self.changed_source_files[0]

    @cached_property
    def changed_source_files(self):
        """
        Returns a tuple of changed and removed source files in the project:
        (changed_files, removed_files)
        """
        source_resources_repo = self.db_project.source_repository

        if not source_resources_repo:
            raise MissingSourceRepository(self.db_project)

        source_directory = self.source_directory_path
        last_revision = source_resources_repo.get_last_synced_revisions()

        modified_files, removed_files = get_changed_files(
            source_resources_repo.type, source_directory, last_revision
        )

        # Unify filesystem and data model file extensions
        if not self.configuration:
            modified_files = map(source_to_locale_path, modified_files)
            removed_files = map(source_to_locale_path, removed_files)

        if source_resources_repo.source_repo or not last_revision:

            def get_path(path):
                return (path, [])

        else:
            relative_source_path = source_directory[
                len(source_resources_repo.checkout_path) :
            ].lstrip(os.sep)

            def get_path(path):
                return (path[len(relative_source_path) :].lstrip(os.sep), [])

        return dict(map(get_path, modified_files)), dict(map(get_path, removed_files))

    @cached_property
    def changed_locales_files(self):
        """
        Map of changed files and locales they were changed for.
        """
        files = {}

        # VCS changes
        repos = self.db_project.translation_repositories()
        if self.repo_locales:
            repos = repos.filter(pk__in=self.repo_locales.keys())

        for repo in repos:
            if repo.multi_locale:
                locales = (
                    self.repo_locales[repo.pk]
                    if self.repo_locales
                    else self.db_project.locales.all()
                )
                for locale in locales:
                    changed_files = get_changed_files(
                        repo.type,
                        repo.locale_checkout_path(locale),
                        repo.get_last_synced_revisions(locale.code),
                    )[0]

                    for path in changed_files:
                        files.setdefault(path, []).append(locale)
            else:
                changed_files = get_changed_files(
                    repo.type, repo.checkout_path, repo.get_last_synced_revisions()
                )[0]

                log.info(
                    "Changed files in {} repository, all: {}".format(
                        self.db_project, changed_files
                    )
                )

                # Include only relevant (localizable) files
                if self.configuration:
                    files = self.get_relevant_files_with_config(changed_files)
                else:
                    files = self.get_relevant_files_without_config(
                        changed_files, self.locale_path_locales(repo.checkout_path)
                    )

        log.info(
            "Changed files in {} repository, relevant for enabled locales: {}".format(
                self.db_project, files
            )
        )

        # DB changes
        vcs = files
        db = self.db_project.changed_resources(self.now)
        for path in set(list(vcs.keys()) + list(db.keys())):
            if path in vcs and path in db:
                vcs[path] = set(list(vcs[path]) + list(db[path]))

            else:
                vcs[path] = vcs[path] if path in vcs else db[path]

        return files

    @cached_property
    def changed_config_files(self):
        """
        A set of the changed project config files.
        """
        config_files = {
            pc.path.replace(os.path.join(self.source_directory_path, ""), "")
            for pc in self.configuration.parsed_configuration.configs
        }
        changed_files = set(self.changed_source_files[0])
        return changed_files.intersection(config_files)

    def get_relevant_files_with_config(self, paths):
        """
        Check if given paths represent localizable files using project configuration.
        Return a dict of relative reference paths of such paths and corresponding Locale
        objects.
        """
        files = {}

        for locale in self.db_project.locales.all():
            for path in paths:
                absolute_path = os.path.join(self.source_directory_path, path)
                reference_path = self.configuration.reference_path(
                    locale, absolute_path
                )

                if reference_path:
                    relative_reference_path = reference_path[
                        len(self.source_directory_path) :
                    ].lstrip(os.sep)
                    files.setdefault(relative_reference_path, []).append(locale)

        return files

    def get_relevant_files_without_config(self, paths, locale_path_locales):
        """
        Check if given paths represent localizable files by matching them against locale
        repository paths. Return a dict of relative reference paths of such paths and
        corresponding Locale objects.
        """
        files = {}
        locale_paths = locale_path_locales.keys()

        for path in paths:
            if is_hidden(path):
                continue

            for locale_path in locale_paths:
                if path.startswith(locale_path):
                    locale = locale_path_locales[locale_path]
                    path = path[len(locale_path) :].lstrip(os.sep)
                    files.setdefault(path, []).append(locale)
                    break

        return files

    def locale_path_locales(self, repo_checkout_path):
        """
        A map of relative locale directory paths and their respective locales.
        """
        locale_path_locales = {}

        for locale in self.db_project.locales.all():
            locale_directory = self.locale_directory_paths[locale.code]
            path = locale_directory[len(repo_checkout_path) :].lstrip(os.sep)
            path = os.path.join(path, "")  # Ensure the path ends with os.sep
            locale_path_locales[path] = locale

        return locale_path_locales

    @cached_property
    def locale_directory_paths(self):
        """
        A map of locale codes and their absolute directory paths.
        Create locale directory, if not in repository yet.
        """
        locale_directory_paths = {}
        parent_directories = set()

        for locale in self.locales:
            try:
                if self.configuration:
                    locale_directory_paths[locale.code] = self.configuration.l10n_base
                else:
                    locale_directory_paths[locale.code] = locale_directory_path(
                        self.checkout_path,
                        locale.code,
                        parent_directories,
                    )
                parent_directory = get_parent_directory(
                    locale_directory_paths[locale.code]
                )

            except OSError:
                if not self.db_project.has_multi_locale_repositories:
                    source_directory = self.source_directory_path
                    parent_directory = get_parent_directory(source_directory)

                    locale_code = locale.code
                    if uses_undercore_as_separator(parent_directory):
                        locale_code = locale_code.replace("-", "_")

                    locale_directory = os.path.join(parent_directory, locale_code)

                    # For asymmetric formats, create empty folder
                    if is_asymmetric_resource(next(self.relative_resource_paths())):
                        os.makedirs(locale_directory)

                    # For other formats, copy resources from source directory
                    else:
                        shutil.copytree(source_directory, locale_directory)

                        for root, dirnames, filenames in os.walk(locale_directory):
                            for filename in filenames:
                                path = os.path.join(root, filename)
                                if is_resource(filename):
                                    os.rename(path, source_to_locale_path(path))
                                else:
                                    os.remove(path)

                    locale_directory_paths[locale.code] = locale_directory

                else:
                    raise MissingLocaleDirectoryError(
                        f"Directory for locale `{locale.code}` not found"
                    )

            parent_directories.add(parent_directory)

        return locale_directory_paths

    @cached_property
    def resources(self):
        """
        Lazy-loaded mapping of relative paths -> VCSResources that need to be synced:
            * changed in repository
            * changed in Pontoon DB
            * corresponding source file added
            * corresponding source file changed
            * all paths relevant for newly enabled (unsynced) locales

        Waiting until first access both avoids unnecessary file reads
        and allows tests that don't need to touch the resources to run
        with less mocking.
        """
        resources = {}

        log.info(
            "Changed files in {} repository and Pontoon, relevant for enabled locales: {}".format(
                self.db_project, self.changed_files
            )
        )

        for path in self.relative_resource_paths():
            # Syncing translations
            if self.locales:
                # Copy list instead of cloning
                locales = list(self.db_project.unsynced_locales)

                if self.changed_files is not None and (
                    (not self.changed_files or path not in self.changed_files)
                    and path not in self.added_paths
                    and path not in self.changed_paths
                ):
                    if not locales:
                        log.debug(f"Skipping unchanged file: {path}")
                        continue

                else:
                    if (
                        self.changed_files is None
                        or path in self.added_paths
                        or path in self.changed_paths
                    ):
                        locales += self.locales
                    else:
                        locales += self.changed_files[path]

            # Syncing resources
            else:
                if self.changed_files is not None and path not in self.changed_files:
                    log.debug(f"Skipping unchanged resource file: {path}")
                    continue
                locales = []

            locales = {loc for loc in locales if loc in self.locales}
            self.synced_locales.update(locales)

            log.debug(
                "Detected resource file {} for {}".format(
                    path, ",".join([loc.code for loc in locales]) or "source"
                )
            )

            try:
                resources[path] = VCSResource(self, path, locales=locales)
            except ParseError as err:
                log.error(
                    "Skipping resource {path} due to ParseError: {err}".format(
                        path=path, err=err
                    )
                )

        log.info(
            "Relative paths in {} that need to be synced: {}".format(
                self.db_project, resources.keys()
            )
        )

        return resources

    @property
    def entities(self):
        return chain.from_iterable(
            resource.entities.values() for resource in self.resources.values()
        )

    @property
    def checkout_path(self):
        return self.db_project.checkout_path

    @cached_property
    def source_directory_path(self):
        """
        Path to the directory where source strings are stored.

        Paths are identified using a scoring system; more likely
        directory names get higher scores, as do directories with
        formats that only used for source strings.
        """
        source_repository = self.db_project.source_repository

        # If project configuration provided, files could be stored in multiple
        # directories, so we just use the source repository checkout path
        if self.configuration:
            return source_repository.checkout_path

        # If source repository explicitly marked
        if source_repository.source_repo:
            return source_repository.checkout_path

        possible_sources = []
        for root, dirnames, filenames in os.walk(self.checkout_path):
            for dirname in dirnames:
                if dirname in self.SOURCE_DIR_NAMES:
                    score = self.SOURCE_DIR_SCORES[dirname]

                    # Ensure the matched directory contains resources.
                    directory_path = os.path.join(root, dirname)
                    if directory_contains_resources(directory_path):
                        # Extra points for source resources!
                        if directory_contains_resources(
                            directory_path, source_only=True
                        ):
                            score += 3

                        possible_sources.append((directory_path, score))

        if possible_sources:
            return max(possible_sources, key=lambda s: s[1])[0]
        else:
            raise MissingSourceDirectoryError(
                f"No source directory found for project {self.db_project.slug}"
            )

    def relative_resource_paths(self):
        """
        List of all source resource paths, relative to source_directory_path.
        """
        if self.configuration:
            paths = self.resource_paths_with_config()
        else:
            paths = self.resource_paths_without_config()

        for path in paths:
            if not self.configuration:
                path = source_to_locale_path(path)
            yield os.path.relpath(path, self.source_directory_path)

    def resource_paths_with_config(self):
        """
        List of absolute paths for all supported source resources
        as specified through project configuration.
        """
        path = self.source_directory_path
        project_files = self.configuration.get_or_set_project_files(None)

        for root, dirnames, filenames in os.walk(path):
            if is_hidden(root):
                continue

            for filename in filenames:
                absolute_path = os.path.join(root, filename)
                if project_files.match(absolute_path):
                    yield absolute_path

    def resource_paths_without_config(self):
        """
        List of absolute paths for all supported source resources
        found within the given path.
        """
        path = self.source_directory_path

        for root, dirnames, filenames in os.walk(path):
            if is_hidden(root):
                continue

            # Ignore certain files in Mozilla repositories.
            if self.db_project.repository_url in MOZILLA_REPOS:
                filenames = [
                    f for f in filenames if not f.endswith("region.properties")
                ]

            for filename in filenames:
                if is_resource(filename):
                    yield os.path.join(root, filename)
