from django.db import models

from pontoon.base.models.user import User


class PersonalAccessToken(models.Model):
    token_id = models.CharField(max_length=16, unique=True)
    token_hash = models.CharField(max_length=128)  # SHA-256
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="personal_access_tokens"
    )
    note = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
