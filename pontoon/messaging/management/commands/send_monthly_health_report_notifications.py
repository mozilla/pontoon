from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.timezone import now

from pontoon.base.models.user import User
from pontoon.insights.utils import get_monthly_health_report
from pontoon.messaging.notifications import send_notification
from pontoon.settings.base import MONTHLY_CHS_SNAPSHOTS_DAY


class Command(BaseCommand):
    help = "Compiles and sends the monthly locale health report to all admins."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force compilation and send regardless of the current date.",
        )

    def handle(self, *args, **options):
        """
        Sends the monthly Community Health Report to all admins as a notification.

        Compares the two most recent monthly CHS snapshots and reports the locales
        whose score changed by at least MONTHLY_HEALTH_REPORT_CHS_THRESHOLD.

        Only send on the given day of the month or when --force is used.
        """
        if not (options["force"] or now().day == MONTHLY_CHS_SNAPSHOTS_DAY):
            self.stdout.write(
                f"This command can only be run on day {MONTHLY_CHS_SNAPSHOTS_DAY} of the month. Use --force to bypass."
            )
            return

        report = get_monthly_health_report()

        if not report["locale_rows"]:
            self.stdout.write("No locales crossed the health report threshold.")
            return

        description = render_to_string(
            "messaging/notifications/health_report.html", report
        )

        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            send_notification(
                admin,
                recipient=admin,
                verb="ignore",
                description=description,
                category="monthly_health_report",
            )

        self.stdout.write(f"Sent {len(admins)} report notifications.")
