from django.contrib.auth.models import Group
from django.db import models

from pontoon.base import utils
from pontoon.base.aggregated_stats import AggregatedStats
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project


class ProjectLocaleQuerySet(models.QuerySet):
    def visible_for(self, user):
        """
        Filter project locales by the visibility of their projects.
        """
        if user.is_superuser:
            return self

        return self.filter(
            project__visibility=Project.Visibility.PUBLIC,
        )

    def visible(self):
        """
        Visible project locales belong to visible projects.
        """
        return self.filter(
            project__disabled=False,
            project__resources__isnull=False,
            project__system_project=False,
        ).distinct()


class ProjectLocale(models.Model, AggregatedStats):
    """Link between a project and a locale that is active for it."""

    @property
    def aggregated_stats_query(self):
        from pontoon.base.models.translated_resource import TranslatedResource

        return TranslatedResource.objects.filter(
            locale=self.locale, resource__project=self.project
        )

    project = models.ForeignKey(Project, models.CASCADE, related_name="project_locale")
    locale = models.ForeignKey(Locale, models.CASCADE, related_name="project_locale")
    readonly = models.BooleanField(default=False)
    pretranslation_enabled = models.BooleanField(default=False)

    #: Most recent translation approved or created for this project in
    #: this locale.
    latest_translation = models.ForeignKey(
        "Translation",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="project_locale_latest",
    )

    # ProjectLocale contains references to user groups that translate them.
    # Groups store respective permissions for users.
    translators_group = models.ForeignKey(
        Group, models.SET_NULL, related_name="projectlocales", null=True
    )

    # Defines if locale has a translators group for the specific project.
    has_custom_translators = models.BooleanField(
        default=False,
    )

    objects = ProjectLocaleQuerySet.as_manager()

    class Meta:
        unique_together = ("project", "locale")
        ordering = ("pk",)
        permissions = (("can_translate_project_locale", "Can add translations"),)

    def __str__(self):
        return "{project} / {locale}".format(
            project=self.project.name,
            locale=self.locale.code,
        )

    @classmethod
    def get_latest_activity(cls, self, extra=None):
        """
        Get the latest activity within project, locale
        or combination of both.

        :param self: object to get data for,
            instance of Project or Locale
        :param extra: extra filter to be used,
            instance of Project or Locale
        """
        latest_translation = None

        if getattr(self, "fetched_project_locale", None):
            if self.fetched_project_locale:
                latest_translation = self.fetched_project_locale[0].latest_translation

        elif extra is None:
            latest_translation = self.latest_translation

        else:
            project = self if isinstance(self, Project) else extra
            locale = self if isinstance(self, Locale) else extra
            project_locale = utils.get_object_or_none(
                ProjectLocale, project=project, locale=locale
            )

            if project_locale is not None:
                latest_translation = project_locale.latest_translation

        return latest_translation.latest_activity if latest_translation else None
