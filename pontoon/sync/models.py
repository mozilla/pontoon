from django.db import models
from django.utils import timezone

from pontoon.base.models import Project


class Sync(models.Model):
    class Status(models.IntegerChoices):
        IN_PROGRESS = 0
        DONE = 1
        NO_CHANGES = 2
        NO_COMMIT = 10
        PREV_BUSY = 20
        FAIL = -1
        INCOMPLETE = -2

    project = models.ForeignKey(Project, models.CASCADE)
    status = models.IntegerField(choices=Status.choices, default=Status.IN_PROGRESS)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=None, blank=True, null=True)
    error = models.TextField(default="")

    def done(self, status: Status = Status.DONE) -> None:
        self.status = status
        self.end_time = timezone.now()
        self.save(update_fields=["status", "end_time"])

    def fail(self, error: str) -> None:
        self.status = Sync.Status.FAIL
        self.error = error
        self.end_time = timezone.now()
        self.save(update_fields=["status", "error", "end_time"])
