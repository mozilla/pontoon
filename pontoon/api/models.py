from django.db import models

from pontoon.base.models.user import User


class PersonalAccessToken(models.Model):
    token_hash = models.CharField(max_length=128)  # SHA-256
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="personal_access_tokens"
    )
    name = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_used = models.DateTimeField(null=True, blank=True)
    revoked = models.BooleanField(default=False)
