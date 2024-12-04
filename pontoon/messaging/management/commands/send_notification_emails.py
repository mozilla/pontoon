from django.core.management.base import BaseCommand
from django.utils.timezone import now

from pontoon.messaging.emails import send_notification_digest


class Command(BaseCommand):
    help = "Send notifications in a daily and weekly email digests."

    def handle(self, *args, **options):
        send_notification_digest(frequency="Daily")

        # Only send weekly digests on Saturdays
        if now().isoweekday() == 6:
            send_notification_digest(frequency="Weekly")
