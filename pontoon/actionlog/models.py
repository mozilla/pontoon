from django.core.exceptions import ValidationError
from django.db import models


class ActionLog(models.Model):
    class ActionType(models.TextChoices):
        # A translation has been created.
        TRANSLATION_CREATED = "translation:created", "Translation created"
        # A translation has been deleted.
        TRANSLATION_DELETED = "translation:deleted", "Translation deleted"
        # A translation has been approved.
        TRANSLATION_APPROVED = "translation:approved", "Translation approved"
        # A translation has been unapproved.
        TRANSLATION_UNAPPROVED = "translation:unapproved", "Translation unapproved"
        # A translation has been rejected.
        TRANSLATION_REJECTED = "translation:rejected", "Translation rejected"
        # A translation has been unrejected.
        TRANSLATION_UNREJECTED = "translation:unrejected", "Translation unrejected"
        # A comment has been added.
        COMMENT_ADDED = "comment:added", "Comment added"

    action_type = models.CharField(max_length=50, choices=ActionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(
        "auth.User", models.SET_NULL, related_name="actions", null=True
    )

    # Used to track on what translation related actions apply.
    translation = models.ForeignKey(
        "base.Translation", models.CASCADE, blank=True, null=True,
    )

    # Used when a translation has been deleted or a team comment has been added.
    entity = models.ForeignKey("base.Entity", models.CASCADE, blank=True, null=True,)
    locale = models.ForeignKey("base.Locale", models.CASCADE, blank=True, null=True,)

    def validate_action_type_choice(self):
        valid_types = self.ActionType.values
        if self.action_type not in valid_types:
            raise ValidationError(
                'Action type "{}" is not one of the permitted values: {}'.format(
                    self.action_type, ", ".join(valid_types)
                )
            )

    def validate_foreign_keys_per_action(self):
        if self.action_type == self.ActionType.TRANSLATION_DELETED and (
            self.translation or not self.entity or not self.locale
        ):
            raise ValidationError(
                f'For action type "{self.action_type}", `entity` and `locale` are required'
            )

        if self.action_type == self.ActionType.COMMENT_ADDED and not (
            (self.translation and not self.locale and not self.entity)
            or (not self.translation and self.locale and self.entity)
        ):
            raise ValidationError(
                f'For action type "{self.action_type}", either `translation` or `entity` and `locale` are required'
            )

        if (
            self.action_type != self.ActionType.TRANSLATION_DELETED
            and self.action_type != self.ActionType.COMMENT_ADDED
        ) and (not self.translation or self.entity or self.locale):
            raise ValidationError(
                f'For action type "{self.action_type}", only `translation` is accepted'
            )

    def save(self, *args, **kwargs):
        self.validate_action_type_choice()
        self.validate_foreign_keys_per_action()

        super(ActionLog, self).save(*args, **kwargs)
