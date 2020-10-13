from django.db import models

from pontoon.base.models import PRIORITY_CHOICES, Project, Resource


class TagQuerySet(models.QuerySet):
    def serialize(self):
        return [tag.serialize() for tag in self]


class Tag(models.Model):
    slug = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    project = models.ForeignKey(Project, models.CASCADE, blank=True, null=True)
    resources = models.ManyToManyField(Resource)
    priority = models.IntegerField(blank=True, null=True, choices=PRIORITY_CHOICES)

    objects = TagQuerySet.as_manager()

    class Meta(object):
        unique_together = [["slug", "project"]]

    def serialize(self):
        return {
            "slug": self.slug,
            "name": self.name,
            "priority": self.priority,
        }
