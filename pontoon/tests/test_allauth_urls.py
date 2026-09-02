import importlib

from django.test import override_settings

import pontoon.allauth_urls


def _social_branch_url_names():
    """Route names registered when local account creation is disabled.

    `pontoon/allauth_urls.py` branches on AUTHENTICATION_METHOD at import time,
    and the test settings use `django`, so the module has to be reloaded to see
    the branch that deployments actually serve.
    """
    try:
        with override_settings(AUTHENTICATION_METHOD="fxa"):
            importlib.reload(pontoon.allauth_urls)
            return {
                pattern.name
                for pattern in pontoon.allauth_urls.urlpatterns
                if getattr(pattern, "name", None)
            }
    finally:
        importlib.reload(pontoon.allauth_urls)


def test_local_signup_route_is_not_registered():
    """Local account creation should stay disabled with external authentication."""
    assert "account_signup" not in _social_branch_url_names()
