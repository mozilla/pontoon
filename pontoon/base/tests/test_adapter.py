import pytest

from mock import MagicMock

from allauth.socialaccount.models import SocialAccount, SocialLogin

from pontoon.base.adapter import PontoonSocialAdapter


# We have to support customized adapter during the transition of accounts
# between providers


def _get_sociallogin(user, provider):
    """
    Returns an ready sociallogin object for the given auth provider.
    """
    socialaccount = SocialAccount(user=user, uid="1234", provider=provider,)
    socialaccount.extra_data = {"email": user.email}
    sociallogin = SocialLogin()
    sociallogin.account = socialaccount
    return sociallogin


@pytest.fixture
def social_adapter0(request, user_a):
    log_mock = MagicMock()
    adapter = PontoonSocialAdapter()
    sociallogin = _get_sociallogin(user_a, "fxa")
    return user_a, adapter, sociallogin, log_mock


@pytest.mark.django_db
def test_adapter_base_get_connect_normal_auth_account(social_adapter0):
    user, adapter, sociallogin, log_mock = social_adapter0

    log_mock.return_value = False
    adapter.pre_social_login(
        MagicMock(), sociallogin,
    )
    assert sociallogin.account.pk
    assert sociallogin.user == user


@pytest.mark.django_db
def test_adapter_base_connect_existing_account(social_adapter0):
    user, adapter, sociallogin, log_mock = social_adapter0

    adapter.pre_social_login(
        MagicMock(), sociallogin,
    )
    assert sociallogin.account.pk
    assert sociallogin.user == user
