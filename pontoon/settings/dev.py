"""A various settings that enable additional packages that are helpful in day to day development."""

import copy
import re

from . import base


INSTALLED_APPS = base.INSTALLED_APPS + (
    # Provides a special toolbar which helps with tracking performance issues.
    "debug_toolbar",
    # Adds various commands like e.g. shell which has all models loaded by default.
    "django_extensions",
)

# In development, we want to remove the WhiteNoise middleware, because we need
# precise control of static files loading in order to properly load frontend
# resources. See the `pontoon.translate` module.
MIDDLEWARE = tuple(
    middleware
    for middleware in base.MIDDLEWARE
    if middleware != "whitenoise.middleware.WhiteNoiseMiddleware"
) + ("debug_toolbar.middleware.DebugToolbarMiddleware",)

TEMPLATES = copy.copy(base.TEMPLATES)
TEMPLATES[0]["OPTIONS"]["match_regex"] = re.compile(
    r"""
        ^(?!(
            admin|
            debug_toolbar|
            registration|
            account|
            socialaccount|
            graphene|
            rest_framework|
        )/).*\.(
            html|
            jinja|
            js|
        )$
    """,
    re.VERBOSE,
)

GRAPHENE = {"MIDDLEWARE": ["graphene_django.debug.DjangoDebugMiddleware"]}

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

if base.DJANGO_DEBUG_TOOLBAR:
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    }
