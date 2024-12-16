from collections import defaultdict
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Prefetch
from django.utils.timezone import now

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Locale
from pontoon.messaging.emails import (
    send_inactive_contributor_emails,
    send_inactive_manager_emails,
    send_inactive_translator_emails,
)


class Command(BaseCommand):
    help = "Send inactive account reminder emails based on user role and activity."

    def handle(self, *args, **options):
        users = User.objects.filter(
            profile__last_inactive_reminder_sent__isnull=True,
        )

        # Collect managers and translators with their locales
        locales = Locale.objects.prefetch_related(
            Prefetch("managers_group__user_set", to_attr="fetched_managers"),
            Prefetch("translators_group__user_set", to_attr="fetched_translators"),
        )

        managers = defaultdict(set)
        translators = defaultdict(set)
        for locale in locales:
            for user in locale.managers_group.fetched_managers:
                managers[user.pk].add(locale)
            for user in locale.translators_group.fetched_translators:
                translators[user.pk].add(locale)

        # Inactive Contributors:
        # - Contributor role
        # - At least 1 non-Machinery translation submitted to non-system projects
        # - No login for at least INACTIVE_CONTRIBUTOR_PERIOD months
        # - Has not received inactive account reminder in the past
        inactive_contributors = (
            users.exclude(pk__in=managers.keys() | translators.keys())
            .filter(
                translation__entity__resource__project__system_project=False,
                translation__machinery_sources=[],
                last_login__lte=now()
                - timedelta(days=settings.INACTIVE_CONTRIBUTOR_PERIOD * 30),
            )
            .distinct()
        )

        send_inactive_contributor_emails(inactive_contributors)

        # Inactive Translators:
        # - Translator role
        # - 0 translations submitted in INACTIVE_TRANSLATOR_PERIOD months
        # - 0 translations reviewed in INACTIVE_TRANSLATOR_PERIOD months
        # - Has not received inactive account reminder in the past
        active_user_ids = (
            ActionLog.objects.filter(
                action_type__startswith="translation:",
                created_at__gte=now()
                - timedelta(days=settings.INACTIVE_TRANSLATOR_PERIOD * 30),
            )
            .values_list("performed_by", flat=True)
            .distinct()
        )

        inactive_translators = (
            users.filter(
                pk__in=translators.keys(),
            )
            .exclude(
                pk__in=active_user_ids,
            )
            .distinct()
        )

        send_inactive_translator_emails(inactive_translators, translators)

        # Inactive Managers:
        # - Manager role
        # - 0 translations submitted in INACTIVE_MANAGER_PERIOD months
        # - 0 translations reviewed in INACTIVE_MANAGER_PERIOD months
        # - Has not received inactive account reminder in the past
        active_user_ids = (
            ActionLog.objects.filter(
                action_type__startswith="translation:",
                created_at__gte=now()
                - timedelta(days=settings.INACTIVE_MANAGER_PERIOD * 30),
            )
            .values_list("performed_by", flat=True)
            .distinct()
        )

        inactive_managers = (
            users.filter(
                pk__in=managers.keys(),
            )
            .exclude(
                pk__in=active_user_ids,
            )
            .distinct()
        )

        send_inactive_manager_emails(inactive_managers, managers)
