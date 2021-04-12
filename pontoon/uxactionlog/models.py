from django.db import models


class UXActionLog(models.Model):
    action_type = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    experiment = models.CharField(max_length=128)
    data = models.JSONField(default=dict)
