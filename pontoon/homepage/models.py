# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Homepage(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', )
