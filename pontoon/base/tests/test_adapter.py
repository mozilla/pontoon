from mock import MagicMock, patch

from allauth.socialaccount.models import SocialAccount, SocialLogin

from pontoon.base.tests import BaseTestCase, UserFactory
from django_nose.tools import assert_equal, assert_true, assert_false
from pontoon.base.adapter import PontoonSocialAdapter


class AdapterPreLoginTestCase(BaseTestCase):
    """
    We have to support customized adapter during the transition of accounts between
    fxa and persona.
    """
    def setUp(self):
        self.log_mock = MagicMock()
        self.user = UserFactory.create()

        mock_messages = patch('pontoon.base.adapter.messages')
        self.mock_messages = mock_messages.start()
        self.addCleanup(mock_messages.stop)

        self.adapter = PontoonSocialAdapter()

    def get_sociallogin(self, provider):
        """
        Returns an ready sociallogin object for the given auth provider.
        """
        self.sociallogin = SocialLogin()
        self.socialaccount = SocialAccount(
            user=self.user,
            uid='1234',
            provider=provider,
        )
        self.socialaccount.extra_data = {
            'email': self.user.email,
        }
        self.sociallogin.account = self.socialaccount
        return self.sociallogin

    def test_connect_normal_auth_account(self):
        self.log_mock.return_value = False

        self.adapter.pre_social_login(MagicMock(), self.get_sociallogin('fxa'))

        assert_true(self.sociallogin.account.pk)
        assert_equal(self.sociallogin.user, self.user)

    def test_connect_existing_persona_account(self):
        self.log_mock.side_effect = lambda provider: provider == 'persona'

        self.adapter.pre_social_login(MagicMock, self.get_sociallogin('fxa'))

        assert_true(self.sociallogin.account.pk)
        assert_equal(self.sociallogin.user, self.user)

    def test_already_connected_accounts(self):
        self.log_mock.return_value = True

        self.adapter.pre_social_login(MagicMock, self.get_sociallogin('fxa'))
        assert_false(self.mock_messages.called)
