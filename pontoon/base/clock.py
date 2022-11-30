import django
import dotenv
import os

from celery import Celery


# Read dotenv file and inject it's values into the environment
dotenv.load_dotenv(dotenv_path=os.environ.get("DOTENV_PATH"))

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")

# Needed for standalone Django usage
django.setup()

from django.conf import settings  # noqa
from pontoon.machinery.tasks import warm_up_automl_models  # noqa

# Configure Celery using the Django settings
app = Celery()
app.config_from_object("django.conf:settings")


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        settings.GOOGLE_AUTOML_WARMUP_INTERVAL,
        warm_up_automl_models.delay(),
    )
