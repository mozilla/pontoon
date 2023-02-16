"""
Google Cloud AutoML Translation has latency of ~15s, caused by the loading time of a
custom model into the chip. To keep latency low, we need to make regular dummy warmup
requests, which is what this script does.
"""

import django
import dotenv
import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler


# Read dotenv file and inject its values into the environment
dotenv.load_dotenv(dotenv_path=os.environ.get("DOTENV_PATH"))

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")

# Needed for standalone Django usage
django.setup()

from django.conf import settings  # noqa
from pontoon.base.models import Locale  # noqa
from pontoon.machinery.utils import get_google_automl_translation  # noqa


logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)
sched = BlockingScheduler()


@sched.scheduled_job("interval", seconds=settings.GOOGLE_AUTOML_WARMUP_INTERVAL)
def warm_up_automl_models():
    log.info("Google AutoML Warmup process started.")

    locales = Locale.objects.exclude(google_automl_model="").order_by("code")

    for locale in locales:
        get_google_automl_translation("t", locale)
        log.info(f"Google AutoML Warmup for {locale.code} complete.")

    log.info("Google AutoML Warmup process complete for all locales.")


sched.start()
