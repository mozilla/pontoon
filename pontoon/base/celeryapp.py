import os

import dotenv
from celery import Celery


# Read dotenv file and inject it's values into the environment
dotenv.load_dotenv(dotenv_path=os.environ.get("DOTENV_PATH"))

# Set the default Django settings module for `celery`.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")
from django.conf import settings  # noqa


app = Celery("pontoon")


# Configure Celery using the Django settings and autodiscover apps from
# INSTALLED_APPS.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
