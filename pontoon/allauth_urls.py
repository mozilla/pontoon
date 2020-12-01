"""
Pontoon requires a very specific subset of functionality implemented in django allauth.
Because of concerns related to the security concerns it's a better to keep only selected
views and don't allow user to tamper with the state of an account.
"""
import importlib

from django.urls import path
from django.conf import settings
from django.contrib.auth import views

from allauth.account import views as account_views
from allauth.socialaccount import views as socialaccount_views, providers

if settings.AUTHENTICATION_METHOD == "django":
    urlpatterns = [
        path("standalone-login/", views.LoginView.as_view(), name="standalone_login"),
        path(
            "standalone-logout/", views.LogoutView.as_view(), name="standalone_logout",
        ),
    ]
else:
    urlpatterns = [
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

for provider in providers.registry.get_list():
    try:
        prov_mod = importlib.import_module(provider.get_package() + ".urls")
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, "urlpatterns", None)
    if prov_urlpatterns:
        urlpatterns += prov_urlpatterns
