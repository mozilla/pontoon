import logging

from celery import shared_task

from pontoon.base.models import Locale
from pontoon.machinery.utils import get_google_automl_translation


log = logging.getLogger(__name__)


@shared_task(bind=True)
def warm_up_automl_models(self):
    log.info("Google AutoML Warmup process started.")

    locales = Locale.objects.exclude(google_automl_model="").order_by("code")

    for locale in locales:
        get_google_automl_translation("t", locale)
        log.info(f"Google AutoML Warmup for {locale.code} complete.")

    log.info("Google AutoML Warmup process complete for all locales.")
