import logging
import time

from celery import shared_task

from django.db import (
    transaction
)

from pontoon.checks import libraries
from pontoon.checks.utils import get_failed_checks_db_objects
from pontoon.checks.models import (
    Warning,
    Error,
)

from pontoon.base.models import (
    Translation,
)

log = logging.getLogger(__name__)


@shared_task(bind=True)
def bulk_run_checks(self, translations_pks):
    """
    Run checks on translations
    :arg list[int] translations: list of primary keys for translations that should be processed
    :arg int batch_size: Size of batch that should be checked at once by a worker
    """
    start_time = time.time()
    with transaction.atomic():
        query_start = time.time()
        translations = list(
            Translation.objects
            .prefetch_related('entity', 'entity__resource__entities', 'locale')
            .filter(pk__in=translations_pks)
        )

        log.debug("Task[{}]: Translation query time: {}".format(
            self.request.id,
            time.time() - query_start
        ))

        processing_time = time.time()
        warnings, errors = [], []
        for translation in translations:
            batch_warnings, batch_errors = get_failed_checks_db_objects(
                translation,
                libraries.run_checks(
                    translation.entity,
                    translation.locale.code,
                    translation.entity.string,
                    translation.string,
                    use_tt_checks=False
                )
            )
            warnings.extend(batch_warnings)
            errors.extend(batch_errors)

        log.debug("Task[{}]: Processing time: {}".format(
            self.request.id,
            time.time() - processing_time
        ))

        cleaning_time = time.time()
        Warning.objects.filter(translation__pk__in=translations_pks).delete()
        Error.objects.filter(translation__pk__in=translations_pks).delete()

        log.debug("Task[{}]: Cleaning time: {}".format(
            self.request.id,
            time.time() - cleaning_time
        ))

        insert_time = time.time()
        Warning.objects.bulk_create(warnings)
        Error.objects.bulk_create(errors)

        log.debug("Task[{}]: Insert time: {}".format(
            self.request.id,
            time.time() - insert_time
        ))

        log.info("Task[{}]: Processed items: {}, Warnings({}) Errors({}) in {}".format(
            self.request.id,
            len(translations),
            len(warnings),
            len(errors),
            time.time() - start_time
        ))
