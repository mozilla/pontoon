from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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
        # A TranslationMemoryEntry has been deleted.
        TM_ENTRY_DELETED = "tm_entry:deleted", "TranslationMemoryEntry deleted"
        # TranslationMemoryEntries have been edited.
        TM_ENTRIES_EDITED = "tm_entries:edited", "TranslationMemoryEntries edited"
        # TranslationMemoryEntries have been uploaded.
        TM_ENTRIES_UPLOADED = "tm_entries:uploaded", "TranslationMemoryEntries uploaded"

    action_type = models.CharField(max_length=50, choices=ActionType.choices)
    created_at = models.DateTimeField(default=timezone.now)
    performed_by = models.ForeignKey(
        "auth.User", models.SET_NULL, related_name="actions", null=True
    )

    # Used to track translation-related actions.
    translation = models.ForeignKey(
        "base.Translation",
        models.CASCADE,
        blank=True,
        null=True,
    )

    # Used when a translation or TM entry has been deleted, or a team comment has been added.
    entity = models.ForeignKey(
        "base.Entity",
        models.CASCADE,
        blank=True,
        null=True,
    )
    locale = models.ForeignKey(
        "base.Locale",
        models.CASCADE,
        blank=True,
        null=True,
    )

    # Used to track actions related to TM entries.
    tm_entries = models.ManyToManyField(
        "base.TranslationMemoryEntry",
        blank=True,
    )

    # Some action types (e.g. TRANSLATION_CREATED) may trigger other actions
    # (e.g. TRANSLATION_REJECTED) without direct user intervention.
    # The latter actions should have `is_implicit_action` set to `True`.
    is_implicit_action = models.BooleanField(default=False)

    def validate_action_type_choice(self):
        valid_types = self.ActionType.values
        if self.action_type not in valid_types:
            raise ValidationError(
                'Action type "{}" is not one of the permitted values: {}'.format(
                    self.action_type, ", ".join(valid_types)
                )
            )

    def validate_explicit_action_type_choice(self):
        valid_types = [
            self.ActionType.TRANSLATION_UNAPPROVED,
            self.ActionType.TRANSLATION_REJECTED,
        ]
        if self.is_implicit_action and self.action_type not in valid_types:
            raise ValidationError(
                'Action type "{}" is not one of the permitted values for an implicit action: {}'.format(
                    self.action_type, ", ".join(valid_types)
                )
            )

    def validate_foreign_keys_per_action(self):
        if self.action_type in (
            self.ActionType.TRANSLATION_DELETED,
            self.ActionType.TM_ENTRY_DELETED,
        ):
            if self.translation or not self.entity or not self.locale:
                raise ValidationError(
                    f'For action type "{self.action_type}", only `entity` and `locale` are accepted'
                )

        elif self.action_type == self.ActionType.COMMENT_ADDED:
            if not (
                (self.translation and not self.locale and not self.entity)
                or (not self.translation and self.locale and self.entity)
            ):
                raise ValidationError(
                    f'For action type "{self.action_type}", either `translation` or `entity` and `locale` are accepted'
                )

        elif self.action_type in (
            self.ActionType.TRANSLATION_CREATED,
            self.ActionType.TRANSLATION_APPROVED,
            self.ActionType.TRANSLATION_UNAPPROVED,
            self.ActionType.TRANSLATION_REJECTED,
            self.ActionType.TRANSLATION_UNREJECTED,
        ):
            if not self.translation or self.entity or self.locale:
                raise ValidationError(
                    f'For action type "{self.action_type}", only `translation` is accepted'
                )

        elif self.action_type in (
            self.ActionType.TM_ENTRIES_EDITED,
            self.ActionType.TM_ENTRIES_UPLOADED,
        ):
            if self.translation or self.entity or self.locale:
                raise ValidationError(
                    f'For action type "{self.action_type}", only `tm_entries` is accepted'
                )

    def validate_many_to_many_relationships_per_action(self):
        if self.action_type in (
            self.ActionType.TM_ENTRIES_EDITED,
            self.ActionType.TM_ENTRIES_UPLOADED,
        ):
            if not self.tm_entries or self.translation or self.entity or self.locale:
                raise ValidationError(
                    f'For action type "{self.action_type}", only `tm_entries` is accepted'
                )

    def save(self, *args, **kwargs):
        self.validate_action_type_choice()
        self.validate_explicit_action_type_choice()
        self.validate_foreign_keys_per_action()

        super().save(*args, **kwargs)

        self.validate_many_to_many_relationships_per_action()
