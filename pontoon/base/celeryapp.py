import os

import dotenv

import logging.config

from celery import Celery
from celery.signals import setup_logging


# Read dotenv file and inject its values into the environment
dotenv.load_dotenv(dotenv_path=os.environ.get("DOTENV_PATH"))

# Set the default Django settings module for `celery`.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")
from django.conf import settings  # noqa


app = Celery("pontoon")


# Configure Celery using the Django settings and autodiscover apps from
# INSTALLED_APPS.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@setup_logging.connect
def configure_celery_logging(*args, **kwargs):
    """
    Prevent Celery from configuring its own logging (which adds its handler /
    TaskFormatter), and use Django's LOGGING config instead.
    """
    logging.config.dictConfig(settings.LOGGING)
