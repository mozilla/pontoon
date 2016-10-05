import base64
import hashlib

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.encoding import smart_bytes


class PontoonSocialAdapter(DefaultSocialAccountAdapter):
    """
    It's required to merge old accounts created via django-browserid
    with accounts created by django-allauth.
    """

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
        """connect existing accounts with existing accounts."""
        email = sociallogin.account.extra_data.get('email')

        if not email:
            return

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        # Without this adapter, django-allauth can't connect accounts from the old auth
        # system (django-browserid) and requires manual intervention from the user.
        # Because all of our providers use verified emails, we can safely merge
        # accounts if they have the same primary email.
        login_provider = sociallogin.account.provider
        user_providers = [sa.provider for sa in user.socialaccount_set.all()]

        if login_provider not in user_providers:
            sociallogin.account.user = user
            sociallogin.account.save()
            sociallogin.user = user

            message = 'Your Persona account and Firefox Account have been connected.'

            # Merge current Firefox Account with the old Persona account
            if login_provider == 'persona' and request.user.is_authenticated() and not request.user.profile.from_django_browserid:
                current_user = request.user
                current_socialaccount = current_user.socialaccount_set.first()
                current_socialaccount.user = user
                current_socialaccount.save()
                current_user.delete()
                messages.success(request, message)

            if (login_provider == 'fxa' and user.profile.from_django_browserid) or\
                (len(user_providers) == 1 and not user.profile.from_django_browserid):
                messages.success(request, message)

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
