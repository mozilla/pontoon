import logging
import time

from celery import shared_task

from django.db import transaction

from pontoon.base.models import Translation
from pontoon.checks import libraries
from pontoon.checks.utils import get_failed_checks_db_objects
from pontoon.checks.models import (
    Warning,
    Error,
)


log = logging.getLogger(__name__)


@shared_task(bind=True)
def bulk_run_checks(self, translations_pks):
    """
    Run checks on translations
    :arg list[int] translations_pks: list of primary keys for translations that should be processed
    """
    start_time = time.time()
    with transaction.atomic():
        translations = list(
            Translation.objects
            .prefetch_related('entity', 'entity__resource__entities', 'locale')
            .filter(pk__in=translations_pks)
        )

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

        Warning.objects.filter(translation__pk__in=translations_pks).delete()
        Error.objects.filter(translation__pk__in=translations_pks).delete()

        Warning.objects.bulk_create(warnings)
        Error.objects.bulk_create(errors)

        log.info("Task[{}]: Processed items: {}, Warnings({}) Errors({}) in {}".format(
            self.request.id,
            len(translations),
            len(warnings),
            len(errors),
            time.time() - start_time
        ))
