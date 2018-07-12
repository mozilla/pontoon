import logging

from celery import (
    group,
    signature,
)
from django.core.management.base import BaseCommand

from pontoon.base.models import Translation
from pontoon.checks import SUPPORTED_FILES

import pontoon.checks.tasks

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

        parser.add_argument(
            '--with-disabled-projects',
            action='store_true',
            dest='disabled_projects',
            default=False,
            help='Include disabled projects'
        )

        parser.add_argument(
            '--with-obsolete-entities',
            action='store_true',
            dest='obsolete_entities',
            default=False,
            help='Include obsolete entities'
        )

    def handle(self, *args, **options):
        filter_qs = {}

        if not options['disabled_projects']:
            filter_qs['entity__resource__project__disabled'] = False
        else:
            log.debug('Include disabled projects')

        if not options['obsolete_entities']:
            filter_qs['entity__obsolete'] = False
        else:
            log.debug('Include obsolete entities')

        translations_pks = (
            Translation.objects
            .filter(
                entity__resource__format__in=SUPPORTED_FILES,
                **filter_qs
            )
            .values_list('pk', flat=True)
        )

        # Split translations into even batches and send them to Celery workers
        batch_size = int(options['batch_size'])
        tasks_result = group(
            signature(
                'pontoon.checks.tasks.bulk_run_checks',
                args=(translations_pks[i:i + batch_size],)
            )
            for i in xrange(0, len(translations_pks), batch_size)
        ).apply_async()

        tasks_result.get()

