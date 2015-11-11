from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.utils import timezone

from pontoon.base.models import Project, Repository


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
            return repo_logs.aggregate(Max('end_time'))['end_time__max']

    @property
    def finished(self):
        return all(log.finished for log in self.project_sync_logs.all())

    def get_absolute_url(self):
        return reverse('pontoon.sync.logs.details', kwargs={'sync_log_pk': self.pk})


class ProjectSyncLog(BaseLog):
    sync_log = models.ForeignKey(SyncLog, related_name='project_sync_logs')
    project = models.ForeignKey(Project)

    start_time = models.DateTimeField(default=timezone.now)

    @property
    def end_time(self):
        if not self.finished:
            return None
        else:
            aggregate = (self.repository_sync_logs
                            .all()
                            .aggregate(Max('end_time')))
            return aggregate['end_time__max']

    @property
    def finished(self):
        repo_logs = self.repository_sync_logs.all()
        if len(repo_logs) != self.project.repositories.count():
            return False
        else:
            return all(log.finished for log in repo_logs)


class RepositorySyncLog(BaseLog):
    project_sync_log = models.ForeignKey(ProjectSyncLog,
                                         related_name='repository_sync_logs')
    repository = models.ForeignKey(Repository)

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now, blank=True, null=True)

    @property
    def finished(self):
        return self.end_time is not None
