"""
Models for working with remote translation data stored in a VCS.
"""
import logging
import os.path
from itertools import chain

from pontoon.base import SyncError


log = logging.getLogger(__name__)


class VCSProject(object):
    """
    Container for project data that is stored on the filesystem and
    pulled from a remote VCS.
    """
    def __init__(self, db_project):
        """
        Load resource paths from the given db_project and parse them
        for translation data.
        """
        self.db_project = db_project

        self.resources = {}
        for path in db_project.relative_resource_paths():
            self.resources[path] = VCSResource(self, path)

    @property
    def entities(self):
        return chain.from_iterable(
            resource.entities.values() for resource in self.resources.values()
        )


class VCSResource(object):
    """Represents a single resource across multiple locales."""

    def __init__(self, vcs_project, path):
        """
        Load the resource file for each enabled locale and store its
        translations in VCSEntity instances.
        """
        from pontoon.base import formats  # Avoid circular import.

        self.vcs_project = vcs_project
        self.path = path
        self.files = {}
        self.entities = {}

        db_project = vcs_project.db_project

        # Create entities using resources from the source directory,
        source_resource_path = os.path.join(db_project.source_directory_path(), self.path)
        source_resource_file = formats.parse(source_resource_path)
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
        for locale in db_project.locales.all():
            resource_path = os.path.join(
                db_project.locale_directory_path(locale.code),
                self.path
            )
            try:
                resource_file = formats.parse(resource_path, source_resource_path)
            except IOError:
                continue  # File doesn't exist, let's move on

            self.files[locale] = resource_file
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
        return bool(self.translations.get(locale_code, False))


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
