import base64
import hashlib

from allauth.account.adapter import get_adapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.encoding import smart_bytes


class PontoonSocialAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Generates an unique username in the same way as it was done in django-browserid.
        This is required to avoid collisions and the backward compatibility.
        """
        user = super(PontoonSocialAdapter, self).save_user(request, sociallogin, form)
        user.username = base64.urlsafe_b64encode(
            hashlib.sha1(smart_bytes(user.email)).digest()
        ).rstrip(b'=')
        user.save()
        return user

    def pre_social_login(self, request, sociallogin):
        """
        Connect existing Pontoon accounts with newly created django-allauth
        accounts and make sure users can log in to them with both, Persona
        and Firefox Accounts. Because both of these providers use verified
        emails, we can automatically connect accounts with the same email.
        """
        email = sociallogin.account.extra_data.get('email')
        message = 'Your Persona account and Firefox Account have been connected.'
        connecting_accounts = sociallogin.state.get('process') == 'connect' and request.user.is_authenticated()

        if not email:
            return

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            if connecting_accounts:
                messages.success(request, message)
            return

        if connecting_accounts:
            older_account, newer_account = (request.user, user) if request.user.pk < user.pk else (user, request.user)
            if sociallogin.account.provider == 'persona' or user.logged_via('fxa'):

                # If connecting existing persona with a new Firefox Account
                # that was already logged in previously, make sure that the
                # sociallogin.account.user setting doesn't get overriden
                if user.logged_via('fxa'):
                    user = older_account

                newer_account.is_active = False
                newer_account.email = "connected+{}".format(newer_account.email)
                newer_account.socialaccount_set.update(user=older_account)
                newer_account.emailaddress_set.update(user=older_account)
                newer_account.save()

            sociallogin.account.user = older_account
            sociallogin.account.save()
            sociallogin.user = older_account

            adapter = get_adapter(request)
            adapter.login(request, older_account)

        if connecting_accounts or (sociallogin.account.provider == 'fxa' and not user.logged_via('fxa')):
            messages.success(request, message)

        sociallogin.account.user = user
        sociallogin.account.save()
        sociallogin.user = user

    def get_connect_redirect_url(self, request, sociallogin):
        """
        Redirect to the main page if accounts were connected.
        """
        assert request.user.is_authenticated()
        return '/'

    def is_open_for_signup(self, request, sociallogin):
        """
        Disable signups with Persona.
        """
        if sociallogin.account.provider == 'persona':
            return False

        return True
