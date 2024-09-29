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
        )/).*\.(
            html|
            jinja|
            js|
        )$
    """,
    re.VERBOSE,
)

CSP_IMG_SRC = base.CSP_IMG_SRC + ("data:",)
CSP_SCRIPT_SRC = base.CSP_SCRIPT_SRC + (
    "http://ajax.googleapis.com",
    # Needed for GraphiQL
    "https://cdn.jsdelivr.net",
    # Needed for GraphiQL (inline script)
    "'sha256-HHh/PGb5Jp8ck+QB/v7zeWzuHf3vYssM0CBPvYgEHR4='",
)
CSP_STYLE_SRC = base.CSP_STYLE_SRC + (
    # Needed for GraphiQL
    "https://cdn.jsdelivr.net",
)

GRAPHENE = {"MIDDLEWARE": ["graphene_django.debug.DjangoDebugMiddleware"]}
