from __future__ import absolute_import

import base64
import hashlib

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

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
