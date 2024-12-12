from django.contrib import admin

from pontoon.homepage import forms, models


class HomepageAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "created_at",
    )
    form = forms.HomepageForm


admin.site.register(models.Homepage, HomepageAdmin)
