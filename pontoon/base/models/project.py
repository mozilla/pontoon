from os.path import join
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import BooleanField, Case, F, Sum, Value, When
from django.db.models.manager import BaseManager
from django.utils import timezone

from pontoon.base.aggregated_stats import AggregatedStats
from pontoon.base.models.locale import Locale


if TYPE_CHECKING:
    from pontoon.base.models import ProjectLocale, Resource


class Priority(models.IntegerChoices):
    LOWEST = 1, "Lowest"
    LOW = 2, "Low"
    NORMAL = 3, "Normal"
    HIGH = 4, "High"
    HIGHEST = 5, "Highest"


class ProjectSlugHistory(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    old_slug = models.SlugField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class ProjectQuerySet(models.QuerySet):
    def visible_for(self, user):
        """
        The visiblity of projects is determined by the role of the user:
        * Administrators can access all public and private projects
        * Other users can see only public projects
        """
        if user.is_superuser:
            return self

        return self.filter(visibility=Project.Visibility.PUBLIC)

    def available(self):
        """
        Available projects are not disabled and have at least one
        resource defined.
        """
        return self.filter(disabled=False, resources__isnull=False).distinct()

    def visible(self):
        """
        Visible projects are not disabled and have at least one
        resource defined and are not system projects.
        """
        return self.available().filter(system_project=False)

    def force_syncable(self):
        """
        Projects that can be force-synced are not disabled and use repository as their data source type.
        """
        return self.filter(disabled=False, data_source=Project.DataSource.REPOSITORY)

    def syncable(self):
        """
        Syncable projects are same as force-syncable, but must not have sync disabled.
        """
        return self.force_syncable().filter(sync_disabled=False)

    def stats_data(self, locale=None):
        query = (
            self
            if locale is None
            else self.filter(resources__translatedresources__locale=locale)
        )
        tr = "resources__translatedresources"
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

    def stats_data_as_dict(self, locale=None) -> dict[int, dict[str, int]]:
        """Mapping of project `id` to dict with counts."""
        query = self.stats_data(locale)
        data = query.values(
            "id",
            "total",
            "approved",
            "pretranslated",
            "errors",
            "warnings",
            "unreviewed",
            # TODO: Add "missing" string field and prevent recalculation of field in JavaScript
        )
        return {row["id"]: row for row in data if row["total"]}


class Project(models.Model, AggregatedStats):
    @property
    def aggregated_stats_query(self):
        from pontoon.base.models.translated_resource import TranslatedResource

        return TranslatedResource.objects.filter(resource__project=self)

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    locales = models.ManyToManyField(Locale, through="ProjectLocale")

    project_locale: BaseManager["ProjectLocale"]
    resources: BaseManager["Resource"]

    class DataSource(models.TextChoices):
        REPOSITORY = "repository", "Repository"
        DATABASE = "database", "Database"

    data_source = models.CharField(
        max_length=255,
        default=DataSource.REPOSITORY,
        choices=DataSource.choices,
    )
    can_be_requested = models.BooleanField(
        default=True,
        help_text="""
        Allow localizers to request the project for their team.
    """,
    )

    configuration_file = models.CharField(
        null=True,
        blank=True,
        max_length=2000,
        help_text="""
        A path to the optional project configuration file, relative to the
        source string repository.
        """,
    )

    disabled = models.BooleanField(
        default=False,
        help_text="""
        Hide project from the UI and only keep it accessible from the admin.
        Disable the project instead of deleting it to keep translation memory
        and attributions. Also prevents project from syncing with VCS.
    """,
    )

    date_created = models.DateTimeField(default=timezone.now)
    date_disabled = models.DateTimeField(null=True, blank=True)
    date_modified = models.DateTimeField(default=timezone.now)

    sync_disabled = models.BooleanField(
        default=False,
        help_text="""
        Prevent project from syncing with VCS.
    """,
    )

    system_project = models.BooleanField(
        default=False,
        help_text="""
        System projects are built into Pontoon. They are accessible from the
        translate view, but hidden from dashboards.
    """,
    )

    class Visibility(models.TextChoices):
        PRIVATE = "private", "Private"
        PUBLIC = "public", "Public"

    visibility = models.CharField(
        max_length=20,
        default=Visibility.PRIVATE,
        choices=Visibility.choices,
    )

    # Project info
    info = models.TextField("Project info", blank=True)
    deadline = models.DateField(blank=True, null=True)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.LOWEST)
    contact = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_for",
        help_text="""
        L10n driver in charge of the project
    """,
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="""
        Notes only visible in Administration
    """,
    )

    # Most recent translation approved or created for this project.
    latest_translation = models.ForeignKey(
        "Translation",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="project_latest",
    )

    tags_enabled = models.BooleanField(default=True)

    pretranslation_enabled = models.BooleanField(
        default=False,
        help_text="""
        Pretranslate project strings using automated sources
        like translation memory and machine translation.
        """,
    )

    objects = ProjectQuerySet.as_manager()

    class Meta:
        permissions = (("can_manage_project", "Can manage project"),)
        ordering = ("pk",)

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            "pk": self.pk,
            "name": self.name,
            "slug": self.slug,
            "info": self.info,
            "contact": self.contact.serialize() if self.contact else None,
        }

    def save(self, *args, **kwargs):
        if self.pk is not None:
            try:
                if self.disabled != Project.objects.get(pk=self.pk).disabled:
                    self.date_disabled = timezone.now() if self.disabled else None
            except Project.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    @property
    def checkout_path(self):
        """Path where this project's VCS checkouts are located."""
        return join(settings.MEDIA_ROOT, "projects", self.slug)

    def get_latest_activity(self):
        return (
            self.latest_translation.latest_activity if self.latest_translation else None
        )

    def resource_priority_map(self):
        """
        Returns a map of resource paths and highest priorities of resource tags.
        """
        resource_priority = {}

        resource_priority_qs = self.tags.prefetch_related("resources").values(
            "resources__path", "priority"
        )

        for item in resource_priority_qs:
            path = item["resources__path"]
            if (
                path in resource_priority
                and resource_priority[path] >= item["priority"]
            ):
                continue
            resource_priority[path] = item["priority"]

        return resource_priority

    def available_locales_list(self):
        """Get a list of available locale codes."""
        return list(self.locales.all().values_list("code", flat=True))

    def reset_resource_order(self):
        """
        Sorting resources by path is a heavy operation, so we use the Resource.order field
        to represent the alphabetic order of resources in the project.

        This method resets the order field, and should be called when new resources are
        added to or removed from the project.
        """
        from pontoon.base.models.resource import Resource

        ordered_resources = []

        for idx, r in enumerate(self.resources.order_by("path")):
            r.order = idx
            ordered_resources.append(r)

        Resource.objects.bulk_update(ordered_resources, ["order"])
