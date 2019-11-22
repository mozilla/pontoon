from __future__ import absolute_import, unicode_literals

from django.core.exceptions import ValidationError
from django.db import models

from pontoon.base.models import (
    Entity,
    Locale,
    Translation,
    User,
)


class ActionLog(models.Model):
    ACTIONS_TYPES = (
        # A translation has been created.
        ('translation:created', 'Translation created'),

        # A translation has been deleted.
        ('translation:deleted', 'Translation deleted'),

        # A translation has been approved.
        ('translation:approved', 'Translation approved'),

        # A translation has been unapproved.
        ('translation:unapproved', 'Translation unapproved'),

        # A translation has been rejected.
        ('translation:rejected', 'Translation rejected'),

        # A translation has been unrejected.
        ('translation:unrejected', 'Translation unrejected'),
    )

    action_type = models.CharField(max_length=50, choices=ACTIONS_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(User, models.CASCADE)

    # Used to track on what translation related actions apply.
    translation = models.ForeignKey(
        Translation,
        models.CASCADE,
        blank=True,
        null=True,
    )

    # Used when a translation has been deleted.
    entity = models.ForeignKey(
        Entity,
        models.CASCADE,
        blank=True,
        null=True,
    )
    locale = models.ForeignKey(
        Locale,
        models.CASCADE,
        blank=True,
        null=True,
    )


def validate_action_type_choice(sender, instance, **kwargs):
    valid_types = [t[0] for t in sender.ACTIONS_TYPES]
    if instance.action_type not in valid_types:
        raise ValidationError(
            'Action type "{}" is not one of the permitted values: {}'.format(
                instance.action_type,
                ', '.join(valid_types)
            )
        )


models.signals.pre_save.connect(validate_action_type_choice, sender=ActionLog)


def validate_foreign_keys_per_action(sender, instance, **kwargs):
    if (
        instance.action_type == 'translation:deleted'
        and (
            instance.translation
            or not instance.entity
            or not instance.locale
        )
    ):
        raise ValidationError(
            'For action "translation:deleted", `entity` and `locale` are required'
        )

    if (
        instance.action_type != 'translation:deleted'
        and (
            not instance.translation
            or instance.entity
            or instance.locale
        )
    ):
        raise ValidationError(
            'Only `translation` is accepted for action type "{}"'.format(
                instance.action_type
            )
        )


models.signals.pre_save.connect(validate_foreign_keys_per_action, sender=ActionLog)
