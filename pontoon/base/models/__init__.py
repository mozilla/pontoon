from django.db import models
from django.db.models import (
    Q,
    Sum,
)

from pontoon.base import utils
from pontoon.base.models.comment import Comment
from pontoon.base.models.aggregated_stats import AggregatedStats
from pontoon.base.models.entity import Entity, get_word_count
from pontoon.base.models.locale import Locale, LocaleCodeHistory, validate_cldr
from pontoon.base.models.permission_changelog import PermissionChangelog
from pontoon.base.models.project import Priority, Project, ProjectSlugHistory
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.repository import Repository, repository_url_validator
from pontoon.base.models.resource import Resource
from pontoon.base.models.translation import Translation
from pontoon.base.models.translation_memory import TranslationMemoryEntry
from pontoon.base.models.user import User
from pontoon.base.models.user_profile import UserProfile
from pontoon.db import IContainsCollate  # noqa

__all__ = [
    "AggregatedStats",
    "ChangedEntityLocale",
    "Comment",
    "Entity",
    "ExternalResource",
    "Locale",
    "LocaleCodeHistory",
    "PermissionChangelog",
    "Priority",
    "Project",
    "ProjectLocale",
    "ProjectSlugHistory",
    "Repository",
    "Resource",
    "TranslatedResource",
    "Translation",
    "TranslationMemoryEntry",
    "User",
    "UserProfile",
    "get_word_count",
    "repository_url_validator",
    "validate_cldr",
]


class ExternalResource(models.Model):
    """
    Represents links to external project resources like staging websites,
    production websites, development builds, production builds, screenshots,
    langpacks, etc. or team resources like style guides, dictionaries,
    glossaries, etc.
    Has no relation to the Resource class.
    """

    locale = models.ForeignKey(Locale, models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(Project, models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=32)
    url = models.URLField("URL", blank=True)

    def __str__(self):
        return self.name


class TranslatedResourceQuerySet(models.QuerySet):
    def aggregated_stats(self):
        return self.aggregate(
            total=Sum("resource__total_strings"),
            approved=Sum("approved_strings"),
            pretranslated=Sum("pretranslated_strings"),
            errors=Sum("strings_with_errors"),
            warnings=Sum("strings_with_warnings"),
            unreviewed=Sum("unreviewed_strings"),
        )

    def aggregate_stats(self, instance):
        aggregated_stats = self.aggregated_stats()

        instance.total_strings = aggregated_stats["total"] or 0
        instance.approved_strings = aggregated_stats["approved"] or 0
        instance.pretranslated_strings = aggregated_stats["pretranslated"] or 0
        instance.strings_with_errors = aggregated_stats["errors"] or 0
        instance.strings_with_warnings = aggregated_stats["warnings"] or 0
        instance.unreviewed_strings = aggregated_stats["unreviewed"] or 0

        instance.save(
            update_fields=[
                "total_strings",
                "approved_strings",
                "pretranslated_strings",
                "strings_with_errors",
                "strings_with_warnings",
                "unreviewed_strings",
            ]
        )

    def stats(self, project, paths, locale):
        """
        Returns statistics for the given project, paths and locale.
        """
        translated_resources = self.filter(
            locale=locale,
            resource__project__disabled=False,
        )

        if project.slug == "all-projects":
            translated_resources = translated_resources.filter(
                resource__project__system_project=False,
                resource__project__visibility=Project.Visibility.PUBLIC,
            )
        else:
            translated_resources = translated_resources.filter(
                resource__project=project,
            )

            if paths:
                translated_resources = translated_resources.filter(
                    resource__path__in=paths,
                )

        return translated_resources.aggregated_stats()

    def update_stats(self):
        """
        Update stats on a list of TranslatedResource.
        """
        self = self.prefetch_related("resource__project", "locale")

        locales = Locale.objects.filter(
            translatedresources__in=self,
        ).distinct()

        projects = Project.objects.filter(
            resources__translatedresources__in=self,
        ).distinct()

        projectlocales = ProjectLocale.objects.filter(
            project__resources__translatedresources__in=self,
            locale__translatedresources__in=self,
        ).distinct()

        for translated_resource in self:
            translated_resource.calculate_stats(save=False)

        TranslatedResource.objects.bulk_update(
            list(self),
            fields=[
                "total_strings",
                "approved_strings",
                "pretranslated_strings",
                "strings_with_errors",
                "strings_with_warnings",
                "unreviewed_strings",
            ],
        )

        for project in projects:
            project.aggregate_stats()

        for locale in locales:
            locale.aggregate_stats()

        for projectlocale in projectlocales:
            projectlocale.aggregate_stats()


class TranslatedResource(AggregatedStats):
    """
    Resource representation for a specific locale.
    """

    resource = models.ForeignKey(
        Resource, models.CASCADE, related_name="translatedresources"
    )
    locale = models.ForeignKey(
        Locale, models.CASCADE, related_name="translatedresources"
    )

    #: Most recent translation approved or created for this translated
    #: resource.
    latest_translation = models.ForeignKey(
        "Translation",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="resource_latest",
    )

    objects = TranslatedResourceQuerySet.as_manager()

    class Meta:
        unique_together = (("locale", "resource"),)

    def adjust_all_stats(self, *args, **kwargs):
        project = self.resource.project
        locale = self.locale

        project_locale = utils.get_object_or_none(
            ProjectLocale,
            project=project,
            locale=locale,
        )

        self.adjust_stats(*args, **kwargs)
        project.adjust_stats(*args, **kwargs)

        if not project.system_project:
            locale.adjust_stats(*args, **kwargs)

        if project_locale:
            project_locale.adjust_stats(*args, **kwargs)

    def calculate_stats(self, save=True):
        """Update stats, including denormalized ones."""
        resource = self.resource
        locale = self.locale

        entity_ids = Translation.objects.filter(locale=locale).values("entity")
        translated_entities = Entity.objects.filter(
            pk__in=entity_ids, resource=resource, obsolete=False
        )

        # Singular
        translations = Translation.objects.filter(
            entity__in=translated_entities.filter(string_plural=""),
            locale=locale,
        )

        approved = translations.filter(
            approved=True,
            errors__isnull=True,
            warnings__isnull=True,
        ).count()

        pretranslated = translations.filter(
            pretranslated=True,
            errors__isnull=True,
            warnings__isnull=True,
        ).count()

        errors = (
            translations.filter(
                Q(
                    Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                    & Q(errors__isnull=False)
                ),
            )
            .distinct()
            .count()
        )

        warnings = (
            translations.filter(
                Q(
                    Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                    & Q(warnings__isnull=False)
                ),
            )
            .distinct()
            .count()
        )

        unreviewed = translations.filter(
            approved=False,
            rejected=False,
            pretranslated=False,
            fuzzy=False,
        ).count()

        # Plural
        nplurals = locale.nplurals or 1
        for e in translated_entities.exclude(string_plural="").values_list("pk"):
            translations = Translation.objects.filter(
                entity_id=e,
                locale=locale,
            )

            plural_approved_count = translations.filter(
                approved=True,
                errors__isnull=True,
                warnings__isnull=True,
            ).count()

            plural_pretranslated_count = translations.filter(
                pretranslated=True,
                errors__isnull=True,
                warnings__isnull=True,
            ).count()

            if plural_approved_count == nplurals:
                approved += 1
            elif plural_pretranslated_count == nplurals:
                pretranslated += 1
            else:
                plural_errors_count = (
                    translations.filter(
                        Q(
                            Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                            & Q(errors__isnull=False)
                        ),
                    )
                    .distinct()
                    .count()
                )

                plural_warnings_count = (
                    translations.filter(
                        Q(
                            Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                            & Q(warnings__isnull=False)
                        ),
                    )
                    .distinct()
                    .count()
                )

                if plural_errors_count:
                    errors += 1
                elif plural_warnings_count:
                    warnings += 1

            plural_unreviewed_count = translations.filter(
                approved=False, pretranslated=False, fuzzy=False, rejected=False
            ).count()
            if plural_unreviewed_count:
                unreviewed += plural_unreviewed_count

        if not save:
            self.total_strings = resource.total_strings
            self.approved_strings = approved
            self.pretranslated_strings = pretranslated
            self.strings_with_errors = errors
            self.strings_with_warnings = warnings
            self.unreviewed_strings = unreviewed

            return False

        # Calculate diffs to reduce DB queries
        total_strings_diff = resource.total_strings - self.total_strings
        approved_strings_diff = approved - self.approved_strings
        pretranslated_strings_diff = pretranslated - self.pretranslated_strings
        strings_with_errors_diff = errors - self.strings_with_errors
        strings_with_warnings_diff = warnings - self.strings_with_warnings
        unreviewed_strings_diff = unreviewed - self.unreviewed_strings

        self.adjust_all_stats(
            total_strings_diff,
            approved_strings_diff,
            pretranslated_strings_diff,
            strings_with_errors_diff,
            strings_with_warnings_diff,
            unreviewed_strings_diff,
        )
