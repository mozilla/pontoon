"""
WSGI config for Pontoon.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
import os

import dotenv
from django.core.wsgi import get_wsgi_application
from wsgi_sslify import sslify

_dirname = os.path.dirname
ROOT = _dirname(_dirname(os.path.abspath(__file__)))


def path(*args):
    return os.path.join(ROOT, *args)


# Read .env file and inject it's values into the environment
if "DOTENV_PATH" in os.environ:
    dotenv.read_dotenv(os.environ.get("DOTENV_PATH"))
elif os.path.isfile(path(".env")):
    dotenv.read_dotenv(path(".env"))
elif os.path.isfile(path(".env", ".env")):
    dotenv.read_dotenv(path(".env", ".env"))


# Set settings env var before importing whitenoise as it depends on
# some settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")

# sslify sets a Strict-Transport-Security header,
# which instructs browsers to always use HTTPS.
application = sslify(get_wsgi_application())
