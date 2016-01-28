"""
Contains authorization backends for accounts in the pontoon.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailModelBackend(ModelBackend):
    """
    Default Model backend supports new structure of User models. Unfortunately,
    migration would require a few manual and potentially dangerous moves to migrate
    database schema.
    However, all what we currently need is an authentication via Email field.
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            User().set_password(password)
        return None
