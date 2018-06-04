import pytest

from mock import patch, MagicMock

from allauth.socialaccount.models import SocialAccount, SocialLogin

from pontoon.base.adapter import PontoonSocialAdapter


# We have to support customized adapter during the transition of accounts
# between fxa and persona.

def _get_sociallogin(user, provider):
    """
    Returns an ready sociallogin object for the given auth provider.
    """
    socialaccount = SocialAccount(
        user=user,
        uid='1234',
        provider=provider,
    )
    socialaccount.extra_data = {'email': user.email}
    sociallogin = SocialLogin()
    sociallogin.account = socialaccount
    return sociallogin


@pytest.fixture
def social_adapter0(request, user_a):
    log_mock = MagicMock()
    adapter = PontoonSocialAdapter()
    sociallogin = _get_sociallogin(user_a, 'fxa')
    mock_messages = patch('pontoon.base.adapter.messages')
    mock_messages = mock_messages.start()
    request.addfinalizer(mock_messages.stop)
    return user_a, adapter, sociallogin, log_mock, mock_messages


@pytest.mark.django_db
def test_adapter_base_get_connect_normal_auth_account(social_adapter0):
    user, adapter, sociallogin, log_mock, mock_messages = social_adapter0

    log_mock.return_value = False
    adapter.pre_social_login(
        MagicMock(),
        sociallogin,
    )
    assert sociallogin.account.pk
    assert sociallogin.user == user


@pytest.mark.django_db
def test_adapter_base_connect_existing_persona_account(social_adapter0):
    user, adapter, sociallogin, log_mock, mock_messages = social_adapter0

    log_mock.side_effect = lambda provider: provider == 'persona'
    adapter.pre_social_login(
        MagicMock(),
        sociallogin,
    )
    assert sociallogin.account.pk
    assert sociallogin.user == user


@pytest.mark.django_db
def test_adapter_base_already_connected_accounts(social_adapter0):
    user, adapter, sociallogin, log_mock, mock_messages = social_adapter0

    log_mock.return_value = True
    adapter.pre_social_login(
        MagicMock(),
        sociallogin,
    )
    assert mock_messages.called is False
