from __future__ import absolute_import, unicode_literals

from django.db import models

from pontoon.base.models import (
    Entity,
    Locale,
    Translation,
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
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # Used to track on what translation related actions apply.
    translation = models.ForeignKey(
        Translation,
        on_delete=models.CASCADE,
        blank=True,
    )

    # Used when a translation has been deleted.
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        blank=True,
    )
    locale = models.ForeignKey(
        Locale,
        on_delete=models.CASCADE,
        blank=True,
    )
