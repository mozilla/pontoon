from django.contrib.auth.models import Group
from django.db import models
from django.db.models import BooleanField, Case, F, Sum, Value, When

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

    def stats_data(self, project=None, locale=None):
        if project:
            query = self.filter(
                locale__translatedresources__resource__project=project
            ).prefetch_related("locale")
            tr = "locale__translatedresources"
        elif locale:
            query = self.filter(
                project__resources__translatedresources__locale=locale,
                project__disabled=False,
                project__system_project=False,
                project__visibility="public",
            ).prefetch_related("project")
            tr = "project__resources__translatedresources"
        return query.annotate(
            total=Sum(f"{tr}__total_strings", default=0),
            approved=Sum(f"{tr}__approved_strings", default=0),
            pretranslated=Sum(f"{tr}__pretranslated_strings", default=0),
            errors=Sum(f"{tr}__strings_with_errors", default=0),
            warnings=Sum(f"{tr}__strings_with_warnings", default=0),
            unreviewed=Sum(f"{tr}__unreviewed_strings", default=0),
        ).annotate(
            missing=F("total")
            - F("approved")
            - F("pretranslated")
            - F("errors")
            - F("warnings"),
            is_complete=Case(
                When(
                    total=F("approved") + F("warnings"),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )


class ProjectLocale(models.Model, AggregatedStats):
    """Link between a project and a locale that is active for it."""

    @property
    def aggregated_stats_query(self):
        from pontoon.base.models.translated_resource import TranslatedResource

        return TranslatedResource.objects.current().filter(
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
