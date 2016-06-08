from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.utils import timezone

from pontoon.base.models import Project, Repository
from pontoon.base.utils import latest_datetime


class BaseLog(models.Model):
    @property
    def duration(self):
        if self.end_time is not None:
            return self.end_time - self.start_time
        else:
            return None

    class Meta:
        abstract = True


class SyncLog(BaseLog):
    start_time = models.DateTimeField(default=timezone.now)

    @property
    def end_time(self):
        if not self.finished:
            return None
        else:
            repo_logs = RepositorySyncLog.objects.filter(project_sync_log__sync_log=self)
            repo_end = repo_logs.aggregate(Max('end_time'))['end_time__max']

            skipped_end = self.project_sync_logs.aggregate(
                Max('skipped_end_time')
            )['skipped_end_time__max']

            return latest_datetime([repo_end, skipped_end])

    @property
    def finished(self):
        return all(log.finished for log in self.project_sync_logs.all())

    def get_absolute_url(self):
        return reverse('pontoon.sync.logs.details', kwargs={'sync_log_pk': self.pk})


class ProjectSyncLog(BaseLog):
    sync_log = models.ForeignKey(SyncLog, related_name='project_sync_logs')
    project = models.ForeignKey(Project)

    start_time = models.DateTimeField(default=timezone.now)

    skipped = models.BooleanField(default=False)
    skipped_end_time = models.DateTimeField(default=None, blank=True, null=True)

    @property
    def end_time(self):
        if self.skipped:
            return self.skipped_end_time
        elif self.finished:
            aggregate = (self.repository_sync_logs
                            .all()
                            .aggregate(Max('end_time')))
            return aggregate['end_time__max']
        else:
            return None

    # Possible sync status. May eventually become a model field.
    IN_PROGRESS = 0
    SKIPPED = 1
    SYNCED = 2

    @property
    def status(self):
        """Return a constant for the current status of this sync."""
        if not self.finished:
            return self.IN_PROGRESS
        elif self.skipped:
            return self.SKIPPED
        else:
            return self.SYNCED

    @property
    def finished(self):
        if self.skipped:
            return True

        repo_logs = self.repository_sync_logs.all()
        sync_repos = self.project.repositories.exclude(source_repo=True)
        if len(repo_logs) != sync_repos.count():
            return False
        else:
            return all(log.finished for log in repo_logs)

    def skip(self, end_time=None):
        """Marks current project sync log as skipped"""
        self.skipped = True
        self.skipped_end_time = end_time or timezone.now()
        self.save(update_fields=('skipped', 'skipped_end_time'))


class RepositorySyncLog(BaseLog):
    project_sync_log = models.ForeignKey(ProjectSyncLog,
                                         related_name='repository_sync_logs')
    repository = models.ForeignKey(Repository)

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=None, blank=True, null=True)

    @property
    def finished(self):
        return self.end_time is not None

    def end(self):
        self.repository.set_current_last_synced_revisions()
        self.end_time = timezone.now()
        self.save(update_fields=['end_time'])
