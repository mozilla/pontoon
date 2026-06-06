from typing import TYPE_CHECKING, cast

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from pontoon.base.models.user import User
from pontoon.base.user_utils import gravatar_url, user_banner


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
        locale = self.locale or cast("Translation", self.translation).locale
        author = self.author
        return {
            "author": author.name_or_email if author else "",
            "username": author.username if author else "",
            "user_banner": user_banner(author, locale, project_contact)
            if author
            else "",
            "user_gravatar_url_small": gravatar_url(author) if author else "",
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
