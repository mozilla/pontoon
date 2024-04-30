import logging
from os.path import join

from pontoon.sync.exceptions import ParseError
from pontoon.sync.utils import locale_to_source_path

log = logging.getLogger(__name__)


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
        source_resource_path = join(vcs_project.source_directory_path, self.path)
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
                    locale,
                    source_resource_path,
                )
                if resource_path is None:
                    continue
            else:
                resource_path = join(locale_directory, self.path)

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
