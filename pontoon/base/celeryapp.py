import os

import dotenv
from celery import Celery


_dirname = os.path.dirname
ROOT = _dirname(_dirname(_dirname(os.path.abspath(__file__))))


def path(*args):
    return os.path.join(ROOT, *args)


# Read .env file and inject it's values into the environment
if "DOTENV_PATH" in os.environ:
    dotenv.read_dotenv(os.environ.get("DOTENV_PATH"))
elif os.path.isfile(path(".env")):
    dotenv.read_dotenv(path(".env"))
elif os.path.isfile(path(".env", ".env")):
    dotenv.read_dotenv(path(".env", ".env"))

# Set the default Django settings module for `celery`.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")
from django.conf import settings  # noqa


app = Celery("pontoon")


# Configure Celery using the Django settings and autodiscover apps from
# INSTALLED_APPS.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
