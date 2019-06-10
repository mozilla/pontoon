"""A various settings that enable additional packages that are helpful in day to day development.
"""
from __future__ import absolute_import

import copy
import base

INSTALLED_APPS = base.INSTALLED_APPS + (
    # Provides a special toolbar which helps with tracking performance issues.
    'debug_toolbar',

    # Adds various commands like e.g. shell which has all models loaded by default.
    'django_extensions',

    # sslserver helps to develop features that require HTTPS.
    'sslserver',
)

MIDDLEWARE_CLASSES = base.MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATES = copy.copy(base.TEMPLATES)
TEMPLATES[0]['OPTIONS']['match_regex'] = (
    r'^(?!(admin|debug_toolbar|registration|account|socialaccount)/).*\.(html|jinja|js)$'
)

CSP_SCRIPT_SRC = base.CSP_SCRIPT_SRC + ('http://ajax.googleapis.com',)
CSP_IMG_SRC = base.CSP_IMG_SRC + ('data:',)

GRAPHENE = {
    'MIDDLEWARE': [
        'graphene_django.debug.DjangoDebugMiddleware',
    ]
}
