from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone


if TYPE_CHECKING:
    from pontoon.base.models import Entity, Locale


class ChangedEntityLocale(models.Model):
    """
    ManyToMany model for storing what locales have changed translations for a
    specific entity since the last sync.
    """

    entity: models.ForeignKey["Entity"] = models.ForeignKey("Entity", models.CASCADE)
    locale: models.ForeignKey["Locale"] = models.ForeignKey("Locale", models.CASCADE)
    when = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("entity", "locale")
