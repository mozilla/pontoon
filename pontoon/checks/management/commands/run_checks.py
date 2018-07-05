import logging

from celery import group
from django.core.management.base import BaseCommand

from pontoon.base.models import Translation
from pontoon.checks import SUPPORTED_FILES
from pontoon.checks.tasks import bulk_run_checks

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run checks on all translations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            action='store',
            dest='batch_size',
            default=10000,
            help='Number of translations to check in a single batch/Celery task',
        )

    def handle(self, *args, **options):
        translations_pks = (
            Translation.objects
            .filter(
                entity__resource__format__in=SUPPORTED_FILES
            )
            .values_list('pk', flat=True)
        )
        batch_size = int(options['batch_size'])

        # Split translations into even batches and send them to Celery workers
        tasks_result = group(
            bulk_run_checks.s(translations_pks[i:i + batch_size])
            for i in xrange(0, len(translations_pks), batch_size)
        ).apply_async()

        tasks_result.get()

