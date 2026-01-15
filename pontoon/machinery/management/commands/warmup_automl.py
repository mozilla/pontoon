from django.core.management.base import BaseCommand

from pontoon.base.models import Locale
from pontoon.machinery.utils import get_google_automl_translation


class Command(BaseCommand):
    help = "Collect data needed for the Insights tab"

    def handle(self, *args, **options):
        """
        Google Cloud AutoML Translation has latency of ~15s, caused by the loading time of a
        custom model into the chip. To keep latency low, we need to make regular dummy warmup
        requests, which is what this management command does.
        """
        self.stdout.write("Google AutoML Warmup process started.")

        locales = Locale.objects.exclude(google_automl_model="").order_by("code")

        for locale in locales:
            get_google_automl_translation("t", locale)
            self.stdout.write(f"Google AutoML Warmup for {locale.code} complete.")

        self.stdout.write("Google AutoML Warmup process complete for all locales.")
