import logging

from django.core.management.base import BaseCommand

from pontoon.base.models import Locale
from pontoon.machinery.utils import get_google_automl_translation


log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
        The Google AutoML Translation has latency of ~15s caused by the loading time of
        a custom model into the chip. Since there are replicas, the high tail latency
        occurs for first N requests - one replica may successfully load the model, but
        the request may be routed to other replicas which are still loading. Once all
        replicas load the model, the normal latency should be 200 - 500ms.

        Also, since the chips are shared with other models, models gets evicted from the
        chips if they aren't used for a longer period of time, resulting in high latency
        on the next following request.

        To keep latency low, we need to make regular dummy warm-up requests using this
        management command, which needs to run at least every 10 minutes.

        See https://github.com/mozilla/pontoon/issues/2655 for more details.
        """

    def handle(self, *args, **options):
        log.info("Google AutoML Warmup process started.")

        locales = Locale.objects.exclude(google_automl_model="").order_by("code")

        for locale in locales:
            get_google_automl_translation("t", locale)
            log.info(f"Google AutoML Warmup for {locale.code} complete.")

        log.info("Google AutoML Warmup process complete for all locales.")
