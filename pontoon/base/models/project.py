from collections import defaultdict
from os.path import basename, join, normpath
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Prefetch
from django.utils import timezone
from django.utils.functional import cached_property

from pontoon.base import utils
from pontoon.base.models.aggregated_stats import AggregatedStats
from pontoon.base.models.changed_entity_locale import ChangedEntityLocale
from pontoon.base.models.locale import Locale


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

    def prefetch_project_locale(self, locale):
        """
        Prefetch ProjectLocale and latest translation data for given locale.
        """
        from pontoon.base.models.project_locale import ProjectLocale

        return self.prefetch_related(
            Prefetch(
                "project_locale",
                queryset=(
                    ProjectLocale.objects.filter(locale=locale).prefetch_related(
                        "latest_translation__user", "latest_translation__approved_user"
                    )
                ),
                to_attr="fetched_project_locale",
            )
        )

    def get_stats_sum(self):
        """
        Get sum of stats for all items in the queryset.
        """
        return AggregatedStats.get_stats_sum(self)

    def get_top_instances(self):
        """
        Get top instances in the queryset.
        """
        return AggregatedStats.get_top_instances(self)


class Project(AggregatedStats):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    locales = models.ManyToManyField(Locale, through="ProjectLocale")

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

    langpack_url = models.URLField(
        "Language pack URL",
        blank=True,
        null=True,
        help_text="""
        URL pattern for downloading language packs. Leave empty if language packs
        not available for the project. Supports {locale_code} wildcard.
    """,
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
            "langpack_url": self.langpack_url or "",
            "contact": self.contact.serialize() if self.contact else None,
        }

    def save(self, *args, **kwargs):
        """
        When project disabled status changes, update denormalized stats
        for all project locales.
        """
        disabled_changed = False
        visibility_changed = False

        if self.pk is not None:
            try:
                original = Project.objects.get(pk=self.pk)
                if self.visibility != original.visibility:
                    visibility_changed = True
                if self.disabled != original.disabled:
                    disabled_changed = True
                    if self.disabled:
                        self.date_disabled = timezone.now()
                    else:
                        self.date_disabled = None
            except Project.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if disabled_changed or visibility_changed:
            for locale in self.locales.all():
                locale.aggregate_stats()

    def changed_resources(self, now):
        """
        Returns a map of resource paths and their locales
        that where changed from the last sync.
        """
        resources = defaultdict(set)
        changes = ChangedEntityLocale.objects.filter(
            entity__resource__project=self, when__lte=now
        ).prefetch_related("locale", "entity__resource")

        for change in changes:
            resources[change.entity.resource.path].add(change.locale)

        return resources

    @cached_property
    def unsynced_locales(self):
        """
        Project Locales that haven't been synchronized yet.
        """
        return list(
            set(self.locales.all())
            - set(Locale.objects.filter(translatedresources__resource__project=self))
        )

    @property
    def needs_sync(self):
        """
        True if the project has changed since the last sync such that
        another sync is required.
        """
        changes = ChangedEntityLocale.objects.filter(entity__resource__project=self)
        return changes.exists() or self.unsynced_locales

    @property
    def checkout_path(self):
        """Path where this project's VCS checkouts are located."""
        return join(settings.MEDIA_ROOT, "projects", self.slug)

    # For compatibility with the old sync, these properties refer to the
    # first repository by ID.
    def _repo_compat_attr(self, attribute):
        repo = self.repositories.first()
        return getattr(repo, attribute) if repo is not None else None

    @property
    def repository_type(self):
        return self._repo_compat_attr("type")

    @property
    def repository_url(self):
        return self._repo_compat_attr("url")

    @property
    def repository_path(self):
        return self._repo_compat_attr("checkout_path")

    def repository_for_path(self, path):
        """
        Return the repository instance whose checkout contains the given
        path. If no matching repo is found, raise a ValueError.
        """
        repo = utils.first(
            self.repositories.all(), lambda r: path.startswith(r.checkout_path)
        )

        if repo is None:
            raise ValueError(f"Could not find repo matching path {path}.")
        else:
            return repo

    @property
    def has_multi_locale_repositories(self):
        for repo in self.repositories.all():
            if repo.multi_locale:
                return True

        return False

    @property
    def has_single_repo(self):
        return self.repositories.count() == 1

    @cached_property
    def source_repository(self):
        """
        Returns an instance of repository which contains the path to source files.
        """
        if not self.has_single_repo:
            from pontoon.sync.models import VCSProject

            source_directories = VCSProject.SOURCE_DIR_SCORES.keys()

            for repo in self.repositories.all():
                last_directory = basename(normpath(urlparse(repo.url).path))
                if repo.source_repo or last_directory in source_directories:
                    return repo

        return self.repositories.first()

    def translation_repositories(self):
        """
        Returns a list of project repositories containing translations.
        """
        from pontoon.base.models.repository import Repository

        pks = [
            repo.pk
            for repo in self.repositories.all()
            if repo.is_translation_repository
        ]
        return Repository.objects.filter(pk__in=pks)

    def get_latest_activity(self, locale=None):
        from pontoon.base.models.project_locale import ProjectLocale

        return ProjectLocale.get_latest_activity(self, locale)

    def get_chart(self, locale=None):
        from pontoon.base.models.project_locale import ProjectLocale

        return ProjectLocale.get_chart(self, locale)

    def aggregate_stats(self):
        from pontoon.base.models.translated_resource import TranslatedResource

        TranslatedResource.objects.filter(
            resource__project=self, resource__entities__obsolete=False
        ).distinct().aggregate_stats(self)

    @property
    def avg_string_count(self):
        return int(self.total_strings / self.enabled_locales)

    def resource_priority_map(self):
        """
        Returns a map of resource paths and highest priorities of resource tags.
        """
        resource_priority = {}

        resource_priority_qs = self.tag_set.prefetch_related("resources").values(
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
