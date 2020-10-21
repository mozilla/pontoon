import logging

from django.urls import reverse
from django.db import models
from django.db.models import F, Max, Sum
from django.utils import timezone
from django.utils.functional import cached_property

from pontoon.base.models import Project, ProjectLocale, Repository, TranslatedResource
from pontoon.base.utils import latest_datetime


log = logging.getLogger(__name__)


class BaseLog(models.Model):
    @cached_property
    def duration(self):
        if self.end_time is not None:
            return self.end_time - self.start_time
        else:
            return None

    class Meta:
        abstract = True


class SyncLog(BaseLog):
    start_time = models.DateTimeField(default=timezone.now)

    @cached_property
    def end_time(self):
        try:
            repo_logs = RepositorySyncLog.objects.filter(
                project_sync_log__sync_log=self
            )
            repo_end = repo_logs.latest("end_time").end_time

            skipped_end = self.project_sync_logs.aggregate(Max("skipped_end_time"))[
                "skipped_end_time__max"
            ]

            return latest_datetime([repo_end, skipped_end])

        except RepositorySyncLog.DoesNotExist:
            return None

    @cached_property
    def finished(self):
        return all(log.finished for log in self.project_sync_logs.all())

    def get_absolute_url(self):
        return reverse("pontoon.sync.logs.details", kwargs={"sync_log_pk": self.pk})

    def fix_stats(self):
        """
        Recalculate any broken stats when sync task is finished. This is a
        temporary fix for bug 1310668.
        """
        if not self.finished:
            return

        # total_strings missmatch between TranslatedResource & Resource
        translated_resources = []
        tr_source = TranslatedResource.objects.exclude(
            total_strings=F("resource__total_strings")
        ).select_related("resource")
        for t in tr_source:
            t.total_strings = t.resource.total_strings
            translated_resources.append(t)
            log.info(
                "Fix stats: total_strings mismatch for {resource}, {locale}.".format(
                    resource=t.resource, locale=t.locale.code
                )
            )

        TranslatedResource.objects.bulk_update(
            translated_resources, fields=["total_strings"]
        )

        # total_strings missmatch in ProjectLocales within the same project
        for p in Project.objects.available():
            count = (
                ProjectLocale.objects.filter(project=p)
                .values("total_strings")
                .distinct()
                .count()
            )
            if count > 1:
                for pl in ProjectLocale.objects.filter(project=p):
                    pl.aggregate_stats()

        # approved + fuzzy + errors + warnings > total in TranslatedResource
        for t in (
            TranslatedResource.objects.filter(
                resource__project__disabled=False,
                resource__project__sync_disabled=False,
            )
            .annotate(
                total=Sum(
                    F("approved_strings")
                    + F("fuzzy_strings")
                    + F("strings_with_errors")
                    + F("strings_with_warnings")
                )
            )
            .filter(total__gt=F("total_strings"))
        ):
            log.info(
                "Fix stats: total_strings overflow for {resource}, {locale}.".format(
                    resource=t.resource, locale=t.locale.code
                )
            )
            t.calculate_stats()

        log.info("Sync complete.")


class ProjectSyncLog(BaseLog):
    sync_log = models.ForeignKey(
        SyncLog, models.CASCADE, related_name="project_sync_logs"
    )
    project = models.ForeignKey(Project, models.CASCADE)

    start_time = models.DateTimeField(default=timezone.now)

    skipped = models.BooleanField(default=False)
    skipped_end_time = models.DateTimeField(default=None, blank=True, null=True)

    @cached_property
    def end_time(self):
        if self.skipped:
            return self.skipped_end_time
        elif self.finished:
            aggregate = self.repository_sync_logs.all().aggregate(Max("end_time"))
            return aggregate["end_time__max"]
        else:
            return None

    # Possible sync status. May eventually become a model field.
    IN_PROGRESS = 0
    SKIPPED = 1
    SYNCED = 2

    @cached_property
    def status(self):
        """Return a constant for the current status of this sync."""
        if not self.finished:
            return self.IN_PROGRESS
        elif self.skipped:
            return self.SKIPPED
        else:
            return self.SYNCED

    @cached_property
    def finished(self):
        if self.skipped:
            return True

        repo_logs = self.repository_sync_logs.all()
        if len(repo_logs) != 1:
            return False
        else:
            return all(log.finished for log in repo_logs)

    def skip(self, end_time=None):
        """Marks current project sync log as skipped"""
        self.skipped = True
        self.skipped_end_time = end_time or timezone.now()
        self.save(update_fields=("skipped", "skipped_end_time"))
        self.sync_log.fix_stats()


class RepositorySyncLog(BaseLog):
    project_sync_log = models.ForeignKey(
        ProjectSyncLog, models.CASCADE, related_name="repository_sync_logs"
    )
    repository = models.ForeignKey(Repository, models.CASCADE)

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=None, blank=True, null=True)

    @cached_property
    def finished(self):
        return self.end_time is not None

    def end(self):
        self.end_time = timezone.now()
        self.save(update_fields=["end_time"])
        self.project_sync_log.sync_log.fix_stats()
