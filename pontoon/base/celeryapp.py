import os
import warnings

import dotenv
from celery import Celery


_dirname = os.path.dirname
ROOT = _dirname(_dirname(_dirname(os.path.abspath(__file__))))


def path(*args):
    return os.path.join(ROOT, *args)


# Filter out missing .env warning, it's fine if we don't have one.
warnings.filterwarnings("ignore", module="dotenv")

# Read .env file and inject it's values into the environment
dotenv.read_dotenv(path(".env"))

# Set the default Django settings module for `celery`.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")
from django.conf import settings  # noqa


app = Celery("pontoon")


# Configure Celery using the Django settings and autodiscover apps from
# INSTALLED_APPS.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
