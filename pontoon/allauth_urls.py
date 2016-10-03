"""
Pontoon requires a very specific subset of functionality implemented in django allauth.
Because of concerns related to the security concerns it's a better to keep only selected
views and don't allow user to tamper with the state of an account.
"""
from django.conf.urls import url

from allauth.compat import importlib
from allauth.account import views as account_views
from allauth.socialaccount import views as socialaccount_views, providers

urlpatterns = [
    url(r"^login/$", account_views.login, name="account_login"),
    url(r"^logout/$", account_views.logout, name="account_logout"),
    url(r"^inactive/$", account_views.account_inactive, name="account_inactive"),
    url('^social/login/cancelled/$', socialaccount_views.login_cancelled,
        name='socialaccount_login_cancelled'),
    url('^social/login/error/$', socialaccount_views.login_error, name='socialaccount_login_error'),
]

for provider in providers.registry.get_list():
    try:
        prov_mod = importlib.import_module(provider.get_package() + '.urls')
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, 'urlpatterns', None)
    if prov_urlpatterns:
        urlpatterns += prov_urlpatterns
