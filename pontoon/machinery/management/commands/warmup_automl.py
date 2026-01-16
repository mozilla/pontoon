import time

from django.core.management.base import BaseCommand

from pontoon.base.models import Locale
from pontoon.machinery.utils import get_google_automl_translation


class Command(BaseCommand):
    help = "Google Cloud AutoML Translation custom model warmup"

    def handle(self, *args, **options):
        """
        Google Cloud AutoML Translation has latency of ~15s, caused by the loading time of a
        custom model into the chip. To keep latency low, we need to make regular dummy warmup
        requests, which is what this management command does.
        """
        start_time = time.monotonic()
        warmed_locales = []
        self.stdout.write("[Google AutoML Warmup] Process started.")

        locales = Locale.objects.exclude(google_automl_model="").order_by("code")

        for locale in locales:
            get_google_automl_translation("t", locale)
            warmed_locales.append(locale.code)

        elapsed = time.monotonic() - start_time

        self.stdout.write(
            f"[Google AutoML Warmup] Process complete for locales: {', '.join(warmed_locales)}.\n"
            f"[Google AutoML Warmup] Elapsed time: {elapsed:.2f}s."
        )
