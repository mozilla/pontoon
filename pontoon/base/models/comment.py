from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Comment(models.Model):
    author = models.ForeignKey(User, models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    translation = models.ForeignKey(
        "Translation",
        models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
    )
    locale = models.ForeignKey(
        "Locale", models.CASCADE, related_name="comments", blank=True, null=True
    )
    entity = models.ForeignKey(
        "Entity", models.CASCADE, related_name="comments", blank=True, null=True
    )
    content = models.TextField()
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.content

    def serialize(self):
        return {
            "author": self.author.name_or_email,
            "username": self.author.username,
            "user_status": self.author.status(self.locale),
            "user_gravatar_url_small": self.author.gravatar_url(88),
            "created_at": self.timestamp.strftime("%b %d, %Y %H:%M"),
            "date_iso": self.timestamp.isoformat(),
            "content": self.content,
            "pinned": self.pinned,
            "id": self.id,
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
