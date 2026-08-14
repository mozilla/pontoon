from re import sub
from typing import TYPE_CHECKING

from django.contrib.postgres.fields import ArrayField
from django.db import models

from pontoon.base.models.resource import Resource


if TYPE_CHECKING:
    from pontoon.base.models.entity import Entity


class Section(models.Model):
    resource: models.ForeignKey[Resource] = models.ForeignKey(
        Resource, models.CASCADE, related_name="sections"
    )
    key = ArrayField(models.TextField())
    meta = ArrayField(ArrayField(models.TextField(), size=2), default=list)
    comment = models.TextField(blank=True)

    entities: models.QuerySet["Entity"]
    """Actually a RelatedManager"""

    class Meta:
        indexes = [
            models.Index(fields=["resource"]),
            models.Index(fields=["key", "comment"]),
        ]

    def __str__(self):
        cl = sub(r"(?m)^", "# ", self.comment) if self.comment else None
        kl = f"[{'.'.join(self.key)}]" if self.key else None
        return f"{cl}\n{kl}" if cl and kl else kl or cl or ""
