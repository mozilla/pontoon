from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from pontoon.insights.tasks import collect_chs_snapshots


class Command(BaseCommand):
    help = "Collect monthly CHS snapshots for all visible locales."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force collection regardless of the current date.",
        )

    def handle(self, *args, **options):
        """
        Collects per-locale Community Health Score (CHS) metrics, saved as
        LocaleHealthSnapshots.

        The metrics involve:
        - project completion
        - key projects enabled
        - active managers
        - active translators
        - active contributors
        - all contributors
        - new signups

        Only send on the given day of the month or when --force is used.
        """
        if options["force"] or now().day == settings.MONTHLY_CHS_SNAPSHOTS_DAY:
            collect_chs_snapshots.delay()
        else:
            self.stdout.write(
                f"This command can only be run on day {settings.MONTHLY_CHS_SNAPSHOTS_DAY} of the month. Use --force to bypass."
            )
