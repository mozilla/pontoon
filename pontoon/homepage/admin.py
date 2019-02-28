# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


from pontoon.homepage import models
from pontoon.homepage import forms


class HomepageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created_at',)
    form = forms.HomepageForm


admin.site.register(models.Homepage, HomepageAdmin)
