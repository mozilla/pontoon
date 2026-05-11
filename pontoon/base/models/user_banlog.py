from django.contrib.auth.models import User
from django.db import models


class UserBanLog(models.Model):
    """
    Track ban and unban cycle of users.
    """

    class ActionType(models.TextChoices):
        BANNED = "banned", "Banned"
        UNBANNED = "unbanned", "Unbanned"

    action_type = models.CharField(max_length=10, choices=ActionType.choices)
    performed_by = models.ForeignKey(
        User, models.SET_NULL, null=True, related_name="created_ban_logs"
    )
    performed_on = models.ForeignKey(
        User, models.SET_NULL, null=True, related_name="ban_log"
    )
    action_reason = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User ban log"
        verbose_name_plural = "Users ban logs"
        ordering = ("-created_at",)

    def __str__(self):
        return "User(pk={}) {} User(pk={}) for {}".format(
            self.performed_by_id,
            self.action_type,
            self.performed_on_id,
            self.action_reason,
        )

    __repr__ = __str__
