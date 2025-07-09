from django.db import models

from pontoon.base.models.user import User


class PersonalAccessToken(models.Model):
    token_hash = models.CharField(max_length=128)  # SHA-256
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
