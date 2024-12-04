from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from pontoon.messaging.emails import send_monthly_activity_summary


class Command(BaseCommand):
    help = "Send monthly activity summary emails."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force sending regardless of the current date.",
        )

    def handle(self, *args, **options):
        # Only send on the given day of the month or when --force is used
        if options["force"] or now().day == settings.MONTHLY_ACTIVITY_SUMMARY_DAY:
            send_monthly_activity_summary()
        else:
            self.stdout.write(
                "This command can only be run on the first day of the month. Use --force to bypass."
            )
