# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from pontoon.homepage import models


class HomepageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created_at',)


admin.site.register(models.Homepage, HomepageAdmin)
