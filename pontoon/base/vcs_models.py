"""
Models for working with remote translation data stored in a VCS.
"""
import os.path
from itertools import chain


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
        for locale in db_project.locales.all():
            resource_path = os.path.join(
                db_project.locale_directory_path(locale.code),
                self.path
            )
            try:
                resource_file = formats.parse(resource_path)
            except IOError:
                continue  # File doesn't exist, let's move on

            self.files[locale.code] = resource_file
            for index, translation in enumerate(resource_file.translations):
                # Create the entity if it doesn't yet exist, otherwise
                # append to it.
                if translation.key in self.entities:
                    vcs_entity = self.entities[translation.key]
                else:
                    vcs_entity = VCSEntity(
                        resource=self,
                        key=translation.key,
                        string=translation.source_string,
                        comments=translation.comments,
                        order=index
                    )
                    self.entities[vcs_entity.key] = vcs_entity

                vcs_entity.translations[locale.code] = translation

    def save(self):
        """
        Save changes made to any of the translations in this resource
        back to the filesystem for all locales.
        """
        for locale_code, resource_file in self.files.items():
            resource_file.save()


class VCSEntity(object):
    """
    An Entity is a single string to be translated, and a VCSEntity
    stores the translations for an entity from several locales.
    """
    def __init__(self, resource, key, string, comments, order):
        self.resource = resource
        self.key = key
        self.string = string
        self.translations = {}
        self.comments = comments
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
    def __init__(self, key, source_string, strings, comments, fuzzy, extra):
        self.key = key
        self.source_string = source_string
        self.strings = strings
        self.comments = comments
        self.fuzzy = fuzzy
        self.extra = extra
