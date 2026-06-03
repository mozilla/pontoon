from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from pontoon.insights.tasks import collect_chs_snapshot


class Command(BaseCommand):
    help = "Collect monthly CHS snapshot, one row per locale."

    def handle(self, *args, **options):
        """
        Per-locale Contributor Health Score (CHS) metrics — completion, key-project
        enablement, active managers / translators / contributors, new signups —
        snapshotted once per month. The dashboard reads two snapshots (current month
        and the previous one) to render month-over-month deltas; the Insights tab
        reads 12 snapshots for the trend chart.

        Designed to run on the 1st of every month.
        """
        collect_chs_snapshot(
            end_date=timezone.make_aware(datetime(year=2026, month=5, day=22))
        )
