from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


if TYPE_CHECKING:
    from pontoon.base.models import Entity, Locale, Translation


class Comment(models.Model):
    author: models.ForeignKey[User | None] = models.ForeignKey(
        User, models.SET_NULL, null=True
    )
    timestamp = models.DateTimeField(default=timezone.now)
    translation: models.ForeignKey["Translation | None"] = models.ForeignKey(
        "Translation",
        models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
    )
    locale: models.ForeignKey["Locale | None"] = models.ForeignKey(
        "Locale", models.CASCADE, related_name="comments", blank=True, null=True
    )
    entity: models.ForeignKey["Entity | None"] = models.ForeignKey(
        "Entity", models.CASCADE, related_name="comments", blank=True, null=True
    )
    content = models.TextField()
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.content

    def serialize(self, project_contact):
        locale = self.locale or self.translation.locale
        return {
            "author": self.author.name_or_email,
            "username": self.author.username,
            "user_banner": self.author.banner(locale, project_contact),
            "user_gravatar_url_small": self.author.gravatar_url(88),
            "created_at": self.timestamp.strftime("%b %d, %Y %H:%M"),
            "date_iso": self.timestamp.isoformat(),
            "content": self.content,
            "pinned": self.pinned,
            "id": self.pk,
        }

    def save(self, *args, **kwargs):
        """
        Validate Comments before saving.
        """
        if not (
            (self.translation and not self.locale and not self.entity)
            or (not self.translation and self.locale and self.entity)
        ):
            raise ValidationError("Invalid comment arguments")

        super().save(*args, **kwargs)
