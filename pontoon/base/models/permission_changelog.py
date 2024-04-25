from django.contrib.auth.models import Group, User
from django.db import models


class PermissionChangelog(models.Model):
    """
    Track changes of roles added or removed from a user.
    """

    # Managers can perform various action on a user.
    class ActionType(models.TextChoices):
        # User has been added to a group (e.g. translators, managers).
        ADDED = "added", "Added"
        # User has been removed from a group (e.g. translators, managers).
        REMOVED = "removed", "Removed"

    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    performed_by = models.ForeignKey(
        User, models.SET_NULL, null=True, related_name="changed_permissions_log"
    )
    performed_on = models.ForeignKey(
        User, models.SET_NULL, null=True, related_name="permisions_log"
    )
    group = models.ForeignKey(Group, models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User permissions log"
        verbose_name_plural = "Users permissions logs"
        ordering = ("pk",)

    def __repr__(self):
        return "User(pk={}) {} User(pk={}) from {}".format(
            self.performed_by_id,
            self.action_type,
            self.performed_on_id,
            self.group.name,
        )
