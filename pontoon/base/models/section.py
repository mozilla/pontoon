from re import sub

from django.contrib.postgres.fields import ArrayField
from django.db import models

from pontoon.base.models.resource import Resource


class Section(models.Model):
    resource = models.ForeignKey(Resource, models.CASCADE, related_name="sections")
    key = ArrayField(models.TextField())
    meta = ArrayField(ArrayField(models.TextField(), size=2), default=list)
    comment = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["resource"]),
            models.Index(fields=["key", "comment"]),
        ]

    def __str__(self):
        cl = sub(r"(?m)^", "# ", self.comment) if self.comment else None
        kl = f"[{'.'.join(self.key)}]" if self.key else None
        return f"{cl}\n{kl}" if cl and kl else kl or cl or ""
