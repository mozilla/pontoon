from __future__ import absolute_import

import base64
import hashlib

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
        accounts. Because both of these providers use verified emails,
        we can automatically connect accounts with the same email.
        """
        email = sociallogin.account.extra_data.get('email')

        if not email:
            return

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        if 'fxa' not in [sa.provider for sa in user.socialaccount_set.all()]:
            messages.success(
                request,
                'Your Persona account and Firefox Account have been connected.'
            )

        sociallogin.account.user = user
        sociallogin.account.save()
        sociallogin.user = user
