
from django.db import models

from pontoon.base.models import PRIORITY_CHOICES, Project, Resource


class Tag(models.Model):
    slug = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    project = models.ForeignKey(Project, blank=True, null=True)
    resources = models.ManyToManyField(Resource)
    priority = models.IntegerField(
        blank=True,
        null=True,
        choices=PRIORITY_CHOICES)

    class Meta(object):
        unique_together = [['slug', 'project']]
