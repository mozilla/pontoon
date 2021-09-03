"""
Models for working with remote translation data stored in a VCS.
"""
import logging
import os
import shutil

import requests

from datetime import datetime
from itertools import chain
from pathlib import Path
from urllib.parse import urljoin, urlparse

from compare_locales.paths import (
    ProjectFiles,
    TOMLParser,
)
from django.utils import timezone
from django.utils.functional import cached_property

from pontoon.base import MOZILLA_REPOS
from pontoon.sync.exceptions import ParseError
from pontoon.sync.utils import (
    is_hidden,
    is_resource,
    is_asymmetric_resource,
    get_parent_directory,
    uses_undercore_as_separator,
    directory_contains_resources,
    locale_directory_path,
    locale_to_source_path,
    source_to_locale_path,
)
from pontoon.sync.vcs.repositories import get_changed_files


log = logging.getLogger(__name__)


class DownloadTOMLParser(TOMLParser):
    """
    This wrapper is a workaround for the lack of the shared and persistent filesystem
    on Heroku workers.
    Related: https://bugzilla.mozilla.org/show_bug.cgi?id=1530988
    """

    def __init__(self, checkout_path, permalink_prefix, configuration_file):
        self.checkout_path = os.path.join(checkout_path, "")
        self.permalink_prefix = permalink_prefix
        self.config_path = urlparse(permalink_prefix).path
        self.config_file = configuration_file

    def get_local_path(self, path):
        """Return the directory in which the config file should be stored."""
        local_path = path.replace(self.config_path, "")

        return os.path.join(self.checkout_path, local_path)

    def get_remote_path(self, path):
        """Construct the link to the remote resource based on the local path."""
        remote_config_path = path.replace(self.checkout_path, "")

        return urljoin(self.permalink_prefix, remote_config_path)

    def get_project_config(self, path):
        """Download the project config file and return its local path."""
        local_path = Path(self.get_local_path(path))
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with local_path.open("wb") as f:
            remote_path = self.get_remote_path(path)
            config_file = requests.get(remote_path)
            config_file.raise_for_status()
            f.write(config_file.content)
        return str(local_path)

    def parse(self, path=None, env=None, ignore_missing_includes=True):
        """Download the config file before it gets parsed."""
        return super().parse(
            self.get_project_config(path or self.config_file),
            env,
            ignore_missing_includes,
        )


class MissingRepositoryPermalink(Exception):
    """
    Raised when a project uses project config files and
    its source repository doesn't have the permalink.
    """


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
            # Permalink is required to download project config files.
            if not db_project.source_repository.permalink_prefix:
                raise MissingRepositoryPermalink()

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
                        self.checkout_path, locale.code, parent_directories,
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

            locales = {l for l in locales if l in self.locales}
            self.synced_locales.update(locales)

            log.debug(
                "Detected resource file {} for {}".format(
                    path, ",".join([l.code for l in locales]) or "source"
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


class VCSConfiguration:
    """
    Container for the project configuration, provided by the optional
    configuration file.

    For more information, see:
    https://moz-l10n-config.readthedocs.io/en/latest/fileformat.html.
    """

    def __init__(self, vcs_project):
        self.vcs_project = vcs_project
        self.configuration_file = vcs_project.db_project.configuration_file
        self.project_files = {}

    @cached_property
    def l10n_base(self):
        """
        If project configuration provided, files could be stored in multiple
        directories, so we just use the translation repository checkout path
        """
        return self.vcs_project.db_project.translation_repositories()[0].checkout_path

    @cached_property
    def parsed_configuration(self):
        """Return parsed project configuration file."""
        return DownloadTOMLParser(
            self.vcs_project.db_project.source_repository.checkout_path,
            self.vcs_project.db_project.source_repository.permalink_prefix,
            self.configuration_file,
        ).parse(env={"l10n_base": self.l10n_base})

    def add_locale(self, locale_code):
        """
        Add new locale to project configuration.
        """
        locales = self.parsed_configuration.locales or []
        locales.append(locale_code)
        self.parsed_configuration.set_locales(locales)

        """
        TODO: For now we don't make changes to the configuration file to
        avoid committing it to the VCS. The pytoml serializer messes with the
        file layout (indents and newlines) pretty badly. We should fix the
        serializer and replace the content of this method with the following
        code:

        # Update configuration file
        with open(self.configuration_path, 'r+b') as f:
            data = pytoml.load(f)
            data['locales'].append(locale_code)
            f.seek(0)
            f.write(pytoml.dumps(data, sort_keys=True))
            f.truncate()

        # Invalidate cached parsed configuration
        del self.__dict__['parsed_configuration']

        # Commit configuration file to VCS
        commit_message = 'Update configuration file'
        commit_author = User(
            first_name=settings.VCS_SYNC_NAME,
            email=settings.VCS_SYNC_EMAIL,
        )
        repo = self.vcs_project.db_project.source_repository
        repo.commit(commit_message, commit_author, repo.checkout_path)
        """

    def get_or_set_project_files(self, locale_code):
        """
        Get or set project files for the given locale code. This approach
        allows us to cache the files for later use.

        Also, make sure that the requested locale_code is available in the
        configuration file.
        """
        if (
            locale_code is not None
            and locale_code not in self.parsed_configuration.all_locales
        ):
            self.add_locale(locale_code)

        return self.project_files.setdefault(
            locale_code, ProjectFiles(locale_code, [self.parsed_configuration]),
        )

    def l10n_path(self, locale, reference_path):
        """
        Return l10n path for the given locale and reference path.
        """
        project_files = self.get_or_set_project_files(locale.code)

        m = project_files.match(reference_path)
        return m[0] if m is not None else None

    def reference_path(self, locale, l10n_path):
        """
        Return reference path for the given locale and l10n path.
        """
        project_files = self.get_or_set_project_files(locale.code)

        m = project_files.match(l10n_path)
        return m[1] if m is not None else None

    def locale_resources(self, locale):
        """
        Return a list of Resource instances, which need to be enabled for the
        given locale.
        """
        resources = []
        project_files = self.get_or_set_project_files(locale.code)

        for resource in self.vcs_project.db_project.resources.all():
            absolute_resource_path = os.path.join(
                self.vcs_project.source_directory_path, resource.path,
            )

            if project_files.match(absolute_resource_path):
                resources.append(resource)

        return resources


class VCSResource:
    """Represents a single resource across multiple locales."""

    def __init__(self, vcs_project, path, locales=None):
        """
        Load the resource file for each enabled locale and store its
        translations in VCSEntity instances.
        """
        from pontoon.base.models import Locale
        from pontoon.sync import formats  # Avoid circular import.

        self.vcs_project = vcs_project
        self.path = path
        self.locales = locales or []
        self.files = {}
        self.entities = {}

        # Create entities using resources from the source directory,
        source_resource_path = os.path.join(
            vcs_project.source_directory_path, self.path
        )
        source_resource_path = locale_to_source_path(source_resource_path)
        source_resource_file = formats.parse(
            source_resource_path, locale=Locale.objects.get(code="en-US")
        )

        for index, translation in enumerate(source_resource_file.translations):
            vcs_entity = VCSEntity(
                resource=self,
                key=translation.key,
                context=translation.context,
                string=translation.source_string,
                string_plural=translation.source_string_plural,
                comments=translation.comments,
                group_comments=(
                    translation.group_comments
                    if hasattr(translation, "group_comments")
                    else None
                ),
                resource_comments=(
                    translation.resource_comments
                    if hasattr(translation, "resource_comments")
                    else None
                ),
                source=translation.source,
                order=translation.order or index,
            )
            self.entities[vcs_entity.key] = vcs_entity

        # Fill in translations from the locale resources.
        for locale in locales:
            locale_directory = self.vcs_project.locale_directory_paths[locale.code]

            if self.vcs_project.configuration:
                # Some resources might not be available for this locale
                resource_path = self.vcs_project.configuration.l10n_path(
                    locale, source_resource_path,
                )
                if resource_path is None:
                    continue
            else:
                resource_path = os.path.join(locale_directory, self.path)

            log.debug("Parsing resource file: %s", resource_path)

            try:
                resource_file = formats.parse(
                    resource_path, source_resource_path, locale
                )

            # File doesn't exist or is invalid: log it and move on
            except (OSError, ParseError) as err:
                log.error(
                    "Skipping resource {path} due to {type}: {err}".format(
                        path=path, type=type(err).__name__, err=err
                    )
                )
                continue

            self.files[locale] = resource_file

            log.debug("Discovered %s translations.", len(resource_file.translations))

            for translation in resource_file.translations:
                try:
                    self.entities[translation.key].translations[
                        locale.code
                    ] = translation
                except KeyError:
                    # If the source is missing an entity, we consider it
                    # deleted and don't add it.
                    pass

    def save(self, locale=None):
        """
        Save changes made to any of the translations in this resource
        back to the filesystem for all locales.
        """
        if locale:
            self.files[locale].save(locale)

        else:
            for locale, resource_file in self.files.items():
                resource_file.save(locale)


class VCSEntity:
    """
    An Entity is a single string to be translated, and a VCSEntity
    stores the translations for an entity from several locales.
    """

    def __init__(
        self,
        resource,
        key,
        string,
        source,
        comments,
        group_comments=None,
        resource_comments=None,
        context="",
        string_plural="",
        order=0,
    ):
        self.resource = resource
        self.key = key
        self.string = string
        self.string_plural = string_plural
        self.source = source
        self.comments = comments
        self.group_comments = group_comments or []
        self.resource_comments = resource_comments or []
        self.context = context
        self.order = order
        self.translations = {}

    def has_translation_for(self, locale_code):
        """Return True if a translation exists for the given locale."""
        return locale_code in self.translations


class VCSTranslation:
    """
    A single translation of a source string into another language.

    Since a string can have different translations based on plural
    forms, all of the different forms are stored under self.strings, a
    dict where the keys equal possible values for
    pontoon.base.models.Translation.plural_form and the values equal the
    translation for that plural form.
    """

    def __init__(
        self,
        key,
        strings,
        comments,
        fuzzy,
        context="",
        source_string="",
        source_string_plural="",
        group_comments=None,
        resource_comments=None,
        order=0,
        source=None,
        last_translator=None,
        last_updated=None,
    ):
        self.key = key
        self.context = context
        self.source_string = source_string
        self.source_string_plural = source_string_plural
        self.strings = strings
        self.comments = comments
        self.group_comments = group_comments
        self.resource_comments = resource_comments
        self.fuzzy = fuzzy
        self.order = order
        self.source = source or []
        self.last_translator = last_translator
        self.last_updated = last_updated

    @property
    def extra(self):
        """
        Return a dict of custom properties to store in the database.
        Useful for subclasses from specific formats that have extra data
        that needs to be preserved.
        """
        return {}

    def update_from_db(self, db_translations):
        """
        Update translation with current DB state.
        """
        # If no DB translations are fuzzy, set fuzzy to False.
        # Otherwise, it's true.
        self.fuzzy = any(t for t in db_translations if t.fuzzy)

        if len(db_translations) > 0:
            last_translation = max(
                db_translations,
                key=lambda t: t.date or timezone.make_aware(datetime.min),
            )
            self.last_updated = last_translation.date
            self.last_translator = last_translation.user

        # Replace existing translations with ones from the database.
        self.strings = {db.plural_form: db.string for db in db_translations}
