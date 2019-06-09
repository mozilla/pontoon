"""
WSGI config for Pontoon.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
from __future__ import absolute_import

import os

from django.core.wsgi import get_wsgi_application
from wsgi_sslify import sslify


# Set settings env var before importing whitenoise as it depends on
# some settings.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pontoon.settings')
from whitenoise.django import DjangoWhiteNoise  # noqa

# sslify sets a Strict-Transport-Security header,
# which instructs browsers to always use HTTPS.
application = sslify(DjangoWhiteNoise(get_wsgi_application()))
