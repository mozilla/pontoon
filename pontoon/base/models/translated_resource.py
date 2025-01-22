import logging

from django.db import models
from django.db.models import F, Q, Sum

from .entity import Entity
from .locale import Locale
from .project import Project
from .resource import Resource
from .translation import Translation
from .user import User


log = logging.getLogger(__name__)


class TranslatedResourceQuerySet(models.QuerySet):
    def string_stats(
        self,
        user: User | None = None,
        *,
        count_disabled: bool = False,
        count_system_projects: bool = False,
    ) -> dict[str, int]:
        query = self
        if not count_disabled:
            query = query.filter(resource__project__disabled=False)
        if not count_system_projects:
            query = query.filter(resource__project__system_project=False)
        if user is None or not user.is_superuser:
            query = query.filter(resource__project__visibility="public")
        return query.aggregate(
            total=Sum("total_strings", default=0),
            approved=Sum("approved_strings", default=0),
            pretranslated=Sum("pretranslated_strings", default=0),
            errors=Sum("strings_with_errors", default=0),
            warnings=Sum("strings_with_warnings", default=0),
            unreviewed=Sum("unreviewed_strings", default=0),
        )

    def query_stats(self, project: Project, paths: list[str], locale: Locale):
        """
        Returns statistics for the given project, paths and locale.
        """
        query = self.filter(locale=locale)
        if project.slug == "all-projects":
            return query.string_stats()
        else:
            query = query.filter(resource__project=project)
            if paths:
                query = query.filter(resource__path__in=paths)
            return query.string_stats(count_system_projects=True)

    def calculate_stats(self):
        self = self.prefetch_related("resource__project", "locale")
        for translated_resource in self:
            translated_resource.calculate_stats(save=False)
        TranslatedResource.objects.bulk_update(
            self,
            fields=[
                "total_strings",
                "approved_strings",
                "pretranslated_strings",
                "strings_with_errors",
                "strings_with_warnings",
                "unreviewed_strings",
            ],
        )

        n = len(self)
        log.debug(f"update_stats: {n} translated resource{'' if n == 1 else 's'}")


class TranslatedResource(models.Model):
    """
    Resource representation for a specific locale.
    """

    resource = models.ForeignKey(
        Resource, models.CASCADE, related_name="translatedresources"
    )
    locale = models.ForeignKey(
        Locale, models.CASCADE, related_name="translatedresources"
    )

    total_strings = models.PositiveIntegerField(default=0)
    approved_strings = models.PositiveIntegerField(default=0)
    pretranslated_strings = models.PositiveIntegerField(default=0)
    strings_with_errors = models.PositiveIntegerField(default=0)
    strings_with_warnings = models.PositiveIntegerField(default=0)
    unreviewed_strings = models.PositiveIntegerField(default=0)

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

    def count_total_strings(self):
        entities = Entity.objects.filter(resource=self.resource, obsolete=False)
        total = entities.count()
        plural_count = entities.exclude(string_plural="").count()
        if plural_count:
            total += (self.locale.nplurals - 1) * plural_count
        return total

    def adjust_stats(
        self, before: dict[str, int], after: dict[str, int], tr_created: bool
    ):
        if tr_created:
            self.total_strings = self.count_total_strings()
        self.approved_strings = (
            F("approved_strings") + after["approved"] - before["approved"]
        )
        self.pretranslated_strings = (
            F("pretranslated_strings")
            + after["pretranslated"]
            - before["pretranslated"]
        )
        self.strings_with_errors = (
            F("strings_with_errors") + after["errors"] - before["errors"]
        )
        self.strings_with_warnings = (
            F("strings_with_warnings") + after["warnings"] - before["warnings"]
        )
        self.unreviewed_strings = (
            F("unreviewed_strings") + after["unreviewed"] - before["unreviewed"]
        )
        self.save(
            update_fields=[
                "total_strings",
                "approved_strings",
                "pretranslated_strings",
                "strings_with_errors",
                "strings_with_warnings",
                "unreviewed_strings",
            ]
        )

    def calculate_stats(self, save=True):
        """Update stats, including denormalized ones."""

        self.total_strings = self.count_total_strings()

        translations = Translation.objects.filter(
            entity__resource=self.resource,
            entity__obsolete=False,
            locale=self.locale,
        )

        self.approved_strings = translations.filter(
            approved=True,
            errors__isnull=True,
            warnings__isnull=True,
        ).count()

        self.pretranslated_strings = translations.filter(
            pretranslated=True,
            errors__isnull=True,
            warnings__isnull=True,
        ).count()

        self.strings_with_errors = (
            translations.filter(
                Q(
                    Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                    & Q(errors__isnull=False)
                ),
            )
            .distinct()
            .count()
        )

        self.strings_with_warnings = (
            translations.filter(
                Q(
                    Q(Q(approved=True) | Q(pretranslated=True) | Q(fuzzy=True))
                    & Q(warnings__isnull=False)
                ),
            )
            .distinct()
            .count()
        )

        self.unreviewed_strings = translations.filter(
            approved=False,
            rejected=False,
            pretranslated=False,
            fuzzy=False,
        ).count()

        if save:
            self.save(
                update_fields=[
                    "total_strings",
                    "approved_strings",
                    "pretranslated_strings",
                    "strings_with_errors",
                    "strings_with_warnings",
                    "unreviewed_strings",
                ]
            )
