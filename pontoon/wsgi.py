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


# Read dotenv file and inject it's values into the environment
dotenv.load_dotenv(dotenv_path=os.environ.get("DOTENV_PATH"))

# Set settings env var before importing whitenoise as it depends on
# some settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")

# sslify sets a Strict-Transport-Security header,
# which instructs browsers to always use HTTPS.
application = sslify(get_wsgi_application())
