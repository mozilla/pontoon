
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from pontoon.base.models import Project, Resource


class Tag(models.Model):
    slug = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    project = models.ForeignKey(Project, blank=True, null=True)
    resources = models.ManyToManyField(Resource)
    priority = models.IntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)])

    class Meta(object):
        unique_together = [['slug', 'project']]
