from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from pontoon.sync.models import SyncLog


class Command(BaseCommand):
    help = "Delete sync logs that are older than settings.SYNC_LOG_RETENTION"

    def handle(self, *args, **options):
        delete_date = timezone.now() - timedelta(days=settings.SYNC_LOG_RETENTION)
        (SyncLog.objects.filter(start_time__lte=delete_date).delete())
