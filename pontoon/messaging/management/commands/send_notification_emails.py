from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import datetime

from pontoon.messaging.emails import send_notification_digest


class Command(BaseCommand):
    help = "Send notifications in a daily and weekly email digests."

    def handle(self, *args, **options):
        send_notification_digest(frequency="Daily")

        # Only send weekly digests on Saturdays
        if datetime.today().weekday() == settings.NOTIFICATION_DIGEST_DAY:
            send_notification_digest(frequency="Weekly")
