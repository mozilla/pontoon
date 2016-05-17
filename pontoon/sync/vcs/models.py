"""
Models for working with remote translation data stored in a VCS.
"""
import logging
import os.path

from itertools import chain
from datetime import datetime

from django.utils import timezone
from django.utils.functional import cached_property

from pontoon.base import MOZILLA_REPOS
from pontoon.sync.exceptions import ParseError
from pontoon.sync.utils import (
    is_hidden,
    directory_contains_resources,
    is_resource,
    locale_directory_path,
    relative_source_path,
)
from pontoon.sync.vcs.repositories import get_changed_files


log = logging.getLogger(__name__)


class MissingSourceRepository(Exception):
    """
    Exception is called when project can't find the repository
    which contains source files.
    """


class MissingSourceDirectoryError(Exception):
    """Raised when sync can't find the source directory for the locales."""


class VCSProject(object):
    """
    Container for project data that is stored on the filesystem and
    pulled from a remote VCS.
    """
    SOURCE_DIR_SCORES = {
        'templates': 3,
        'en-US': 2,
        'en': 1
    }
    SOURCE_DIR_NAMES = SOURCE_DIR_SCORES.keys()

    def __init__(self, db_project, locales=None, obsolete_entities_paths=None, full_scan=False):
        """
        Load resource paths from the given db_project and parse them
        for translation data.

        :param Project db_project:
            Project model instance for the project we're going to be
            reading files for.
        :param list locales:
            List of Locale model instances for the locales that we want
            to parse. Defaults to parsing resources for all enabled
            locales on the project.
        :param list obsolete_entities_paths:
            List of paths to remove translations of obsolete entities from
        :param bool full_scan:
            Scans all resources in repository
        """
        self.db_project = db_project
        self.locales = locales if locales is not None else db_project.locales.all()
        self.obsolete_entities_paths = obsolete_entities_paths or []
        self.full_scan = full_scan
        self.synced_locales = set()

    @cached_property
    def changed_files(self):
        if self.full_scan:
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

        source_directory = self.source_directory_path()

        if source_resources_repo.last_synced_revisions:
            last_revision = source_resources_repo.last_synced_revisions.get('single_locale')
        else:
            last_revision = None

        modified_files, removed_files = get_changed_files(source_resources_repo.type, source_directory, last_revision)

        if source_resources_repo.source_repo or not last_revision:
            get_path = lambda path: (path, [])
        else:
            relative_source_path = source_directory[len(source_resources_repo.checkout_path):].lstrip(os.sep)
            get_path = lambda path: (path[len(relative_source_path):].lstrip(os.sep), [])

        return dict(map(get_path, modified_files)), dict(map(get_path, removed_files))

    @cached_property
    def changed_locales_files(self):
        """
        Map of repositories and files changed within them after the latest update.
        """
        files = {}

        def find_changed_files(repo, locale=None):
            """
            Returns a dictionary that contains resource paths as keys and their
            list of locales as value.
            """
            if repo.last_synced_revisions:
                last_revision = repo.last_synced_revisions.get(locale.code if locale else 'single_locale')
            else:
                last_revision = None

            # We have to filter out paths that are locale files
            checkout_path = repo.locale_checkout_path(locale) if locale else repo.checkout_path
            return get_changed_files(repo.type, checkout_path, last_revision)[0]

        for repo in self.db_project.repositories.exclude(source_repo=True):
            if repo.multi_locale:
                for locale in self.db_project.locales.all():
                    for path in find_changed_files(repo, locale):
                        files.setdefault(path, []).append(locale)
            else:
                changed_files = find_changed_files(repo)

                for path, locale_path, locale in filter(None, map(lambda x: self.get_path_info(x, repo), changed_files)):
                    path = path[len(locale_path):].lstrip(os.sep)
                    files.setdefault(path, []).append(locale)
        return files


    def get_path_info(self, path, repo):
        """
        Checks if path inside one of locale directories.
        Returns a tuple with information on given path or None if can't find any.
        Tuple contains:
        - path to the given file
        - path to the locale directory
        - locale code
        """
        if is_hidden(path):
            return None

        try:
            locale_path, locale = next((p, l) for p, l in self.locale_directories(repo).items() if path.startswith(p))
        except StopIteration:
            return None

        return path, locale_path, locale

    def locale_directories(self, repo):
        """
        A map of paths to their respective locales.
        """
        locales_paths = {}
        for locale in self.db_project.locales.all():
            path = locale_directory_path(repo.checkout_path, locale.code)[len(repo.checkout_path):].lstrip(os.sep)
            locales_paths[path] = locale
        return locales_paths

    @cached_property
    def resources(self):
        """
        Lazy-loaded mapping of relative paths -> VCSResources.

        Waiting until first access both avoids unnecessary file reads
        and allows tests that don't need to touch the resources to run
        with less mocking.
        """
        resources = {}

        for path in self.relative_resource_paths():
            locales = self.db_project.unsynced_locales

            if (self.changed_files is not None and
                ((not self.changed_files or path not in self.changed_files) and
                    path not in self.obsolete_entities_paths)):
                if not locales:
                    log.debug('Skipping unchanged file: {}'.format(path))
                    continue

            else:
                if self.changed_files is None or path in self.obsolete_entities_paths:
                    locales += self.locales
                else:
                    locales += self.changed_files[path]

            map(self.synced_locales.add, locales)
            log.debug('Resource file {} for {}'.format(path, ','.join([l.code for l in locales])))

            try:
                resources[path] = VCSResource(self, path, locales=locales)
            except ParseError as err:
                log.error('Skipping resource {path} due to ParseError: {err}'.format(
                    path=path, err=err
                ))

        return resources

    @property
    def entities(self):
        return chain.from_iterable(
            resource.entities.values() for resource in self.resources.values()
        )

    @property
    def checkout_path(self):
        return self.db_project.checkout_path

    def source_directory_path(self):
        """
        Path to the directory where source strings are stored.

        Paths are identified using a scoring system; more likely
        directory names get higher scores, as do directories with
        formats that only used for source strings.
        """
        possible_sources = []
        for root, dirnames, filenames in os.walk(self.checkout_path):
            for dirname in dirnames:
                if dirname in self.SOURCE_DIR_NAMES:
                    score = self.SOURCE_DIR_SCORES[dirname]

                    # Ensure the matched directory contains resources.
                    directory_path = os.path.join(root, dirname)
                    if directory_contains_resources(directory_path):
                        # Extra points for source resources!
                        if directory_contains_resources(directory_path, source_only=True):
                            score += 3

                        possible_sources.append((directory_path, score))

        if possible_sources:
            return max(possible_sources, key=lambda s: s[1])[0]
        else:
            raise MissingSourceDirectoryError('No source directory found for project {0}'.format(self.db_project.slug))

    def relative_resource_paths(self):
        """
        List of paths relative to the locale directories returned by
        self.locale_directory_path() for each resource in this project.
        """
        path = self.source_directory_path()
        for absolute_path in self.resources_for_path(path):
            # .pot files in the source directory need to be renamed to
            # .po files for the locale directories.
            if absolute_path.endswith('.pot'):
                absolute_path = absolute_path[:-1]

            yield os.path.relpath(absolute_path, path)

    def resources_for_path(self, path):
        """
        List of paths for all supported resources found within the given
        path.
        """
        for root, dirnames, filenames in os.walk(path):
            if is_hidden(root):
                continue

            # Ignore certain files in Mozilla repositories.
            if self.db_project.repository_url in MOZILLA_REPOS:
                filenames = [f for f in filenames if not f.endswith('region.properties')]

            for filename in filenames:
                if is_resource(filename):
                    yield os.path.join(root, filename)


class VCSResource(object):
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
        source_resource_path = os.path.join(vcs_project.source_directory_path(), self.path)
        source_resource_path = relative_source_path(source_resource_path)
        source_resource_file = formats.parse(source_resource_path, locale=Locale.objects.get(code='en-US'))
        for index, translation in enumerate(source_resource_file.translations):
            vcs_entity = VCSEntity(
                resource=self,
                key=translation.key,
                string=translation.source_string,
                string_plural=translation.source_string_plural,
                comments=translation.comments,
                source=translation.source,
                order=translation.order or index
            )
            self.entities[vcs_entity.key] = vcs_entity

        # Fill in translations from the locale resources.
        for locale in locales:
            resource_path = os.path.join(
                locale_directory_path(vcs_project.checkout_path, locale.code),
                self.path
            )

            log.debug('Parsing resource file: %s', resource_path)

            try:
                resource_file = formats.parse(resource_path, source_resource_path, locale)
            except (IOError, ParseError):
                continue  # File doesn't exist or is invalid, let's move on

            self.files[locale] = resource_file

            log.debug('Discovered %s translations.', len(resource_file.translations))

            for translation in resource_file.translations:
                try:
                    self.entities[translation.key].translations[locale.code] = translation
                except KeyError:
                    # If the source is missing an entity, we consider it
                    # deleted and don't add it.
                    pass

    def save(self):
        """
        Save changes made to any of the translations in this resource
        back to the filesystem for all locales.
        """
        for locale, resource_file in self.files.items():
            resource_file.save(locale)


class VCSEntity(object):
    """
    An Entity is a single string to be translated, and a VCSEntity
    stores the translations for an entity from several locales.
    """
    def __init__(self, resource, key, string, comments, source, string_plural='',
                 order=0):
        self.resource = resource
        self.key = key
        self.string = string
        self.string_plural = string_plural
        self.translations = {}
        self.comments = comments
        self.source = source
        self.order = order

    def has_translation_for(self, locale_code):
        """Return True if a translation exists for the given locale."""
        return locale_code in self.translations


class VCSTranslation(object):
    """
    A single translation of a source string into another language.

    Since a string can have different translations based on plural
    forms, all of the different forms are stored under self.strings, a
    dict where the keys equal possible values for
    pontoon.base.models.Translation.plural_form and the values equal the
    translation for that plural form.
    """
    def __init__(
        self, key, strings, comments, fuzzy,
        source_string='',
        source_string_plural='',
        order=0,
        source=None,
        last_translator=None,
        last_updated=None
    ):
        self.key = key
        self.source_string = source_string
        self.source_string_plural = source_string_plural
        self.strings = strings
        self.comments = comments
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
                key=lambda t: t.date or timezone.make_aware(datetime.min)
            )
            self.last_updated = last_translation.date
            self.last_translator = last_translation.user

        # Replace existing translations with ones from the database.
        self.strings = {
            db.plural_form: db.string for db in db_translations
        }
