# -*- coding: utf-8 -*-
from django.db import models


class Homepage(models.Model):
    text = models.TextField()
    title = models.CharField(max_length=255, default="Pontoon")
    created_at = models.DateTimeField(auto_now_add=True)
