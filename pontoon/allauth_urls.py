"""
Pontoon requires a very specific subset of functionality implemented in django allauth.
Because of concerns related to the security concerns it's a better to keep only selected
views and don't allow user to tamper with the state of an account.
"""

import importlib

from typing import List, Union

from allauth.account import views as account_views
from allauth.socialaccount import providers, views as socialaccount_views

from django.conf import settings
from django.contrib.auth import views
from django.urls import URLPattern, URLResolver, path


def build_provider_urlpatterns() -> List[Union[URLPattern, URLResolver]]:
    provider_urlpatterns: List[Union[URLPattern, URLResolver]] = []
    provider_classes = providers.registry.get_class_list()

    provider_classes = [
        cls for cls in provider_classes if cls.id != "openid_connect"
    ] + [cls for cls in provider_classes if cls.id == "openid_connect"]
    for provider_class in provider_classes:
        prov_mod = importlib.import_module(provider_class.get_package() + ".urls")
        prov_urlpatterns = getattr(prov_mod, "urlpatterns", None)
        if prov_urlpatterns:
            provider_urlpatterns += prov_urlpatterns
    return provider_urlpatterns


if settings.AUTHENTICATION_METHOD == "django":
    urlpatterns = [
        path("standalone-login/", views.LoginView.as_view(), name="standalone_login"),
        path(
            "standalone-logout/",
            views.LogoutView.as_view(),
            name="standalone_logout",
        ),
    ]
else:
    urlpatterns: List[Union[URLPattern, URLResolver]] = [
        path("login/", account_views.login, name="account_login"),
        path("logout/", account_views.logout, name="account_logout"),
        path("inactive/", account_views.account_inactive, name="account_inactive"),
        path(
            "social/login/cancelled/",
            socialaccount_views.login_cancelled,
            name="socialaccount_login_cancelled",
        ),
        path(
            "social/login/error/",
            socialaccount_views.login_error,
            name="socialaccount_login_error",
        ),
    ]
    urlpatterns += build_provider_urlpatterns()
