import logging

from typing import Any

from django.db import models
from django.db.models import Q, Sum

from pontoon.base import utils
from pontoon.base.models.aggregated_stats import AggregatedStats
from pontoon.base.models.entity import Entity
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.resource import Resource
from pontoon.base.models.translation import Translation


log = logging.getLogger(__name__)


class TranslatedResourceQuerySet(models.QuerySet):
    def aggregated_stats(self):
        return self.aggregate(
            total=Sum("total_strings"),
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

        def _log(n: int, thing: str):
            things = thing if n == 1 else f"{thing}s"
            log.debug(f"update_stats: {n} {things}")

        fields = [
            "total_strings",
            "approved_strings",
            "pretranslated_strings",
            "strings_with_errors",
            "strings_with_warnings",
            "unreviewed_strings",
        ]

        self = self.prefetch_related("resource__project", "locale")
        for translated_resource in self:
            translated_resource.calculate_stats(save=False)
        TranslatedResource.objects.bulk_update(self, fields=fields)
        _log(len(self), "translated resource")

        projectlocale_count = 0
        for projectlocale in ProjectLocale.objects.filter(
            project__resources__translatedresources__in=self,
            locale__translatedresources__in=self,
        ).distinct():
            projectlocale.aggregate_stats()
            projectlocale_count += 1
        _log(projectlocale_count, "projectlocale")

        project_count = 0
        for project in Project.objects.filter(
            resources__translatedresources__in=self,
        ).distinct():
            stats: dict[str, Any] = ProjectLocale.objects.filter(
                project=project
            ).aggregated_stats()
            project.total_strings = stats["total_strings"] or 0
            project.approved_strings = stats["approved_strings"] or 0
            project.pretranslated_strings = stats["pretranslated_strings"] or 0
            project.strings_with_errors = stats["strings_with_errors"] or 0
            project.strings_with_warnings = stats["strings_with_warnings"] or 0
            project.unreviewed_strings = stats["unreviewed_strings"] or 0
            project.save(update_fields=fields)
            project_count += 1
        _log(project_count, "project")

        locales = Locale.objects.filter(translatedresources__in=self).distinct()
        for locale in locales:
            stats: dict[str, Any] = ProjectLocale.objects.filter(
                locale=locale,
                project__system_project=False,
                project__visibility=Project.Visibility.PUBLIC,
            ).aggregated_stats()
            locale.total_strings = stats["total_strings"] or 0
            locale.approved_strings = stats["approved_strings"] or 0
            locale.pretranslated_strings = stats["pretranslated_strings"] or 0
            locale.strings_with_errors = stats["strings_with_errors"] or 0
            locale.strings_with_warnings = stats["strings_with_warnings"] or 0
            locale.unreviewed_strings = stats["unreviewed_strings"] or 0
        Locale.objects.bulk_update(locales, fields=fields)
        _log(len(locales), "locale")


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

        if (
            not project.system_project
            and project.visibility == Project.Visibility.PUBLIC
        ):
            locale.adjust_stats(*args, **kwargs)

        if project_locale:
            project_locale.adjust_stats(*args, **kwargs)

    def count_total_strings(self):
        entities = Entity.objects.filter(resource=self.resource, obsolete=False)
        total = entities.count()
        plural_count = entities.exclude(string_plural="").count()
        if plural_count:
            total += (self.locale.nplurals - 1) * plural_count
        return total

    def calculate_stats(self, save=True):
        """Update stats, including denormalized ones."""

        total = self.count_total_strings()

        translations = Translation.objects.filter(
            entity__resource=self.resource,
            entity__obsolete=False,
            locale=self.locale,
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

        if not save:
            self.total_strings = total
            self.approved_strings = approved
            self.pretranslated_strings = pretranslated
            self.strings_with_errors = errors
            self.strings_with_warnings = warnings
            self.unreviewed_strings = unreviewed

            return False

        # Calculate diffs to reduce DB queries
        total_strings_diff = total - self.total_strings
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
