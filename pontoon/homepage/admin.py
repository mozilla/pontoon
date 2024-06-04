from django.contrib import admin
from pontoon.homepage import forms, models


class HomepageAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "created_at",
    )
    form = forms.HomepageForm

    class Media:
        css = {"all": ("css/homepage_admin.css",)}


admin.site.register(models.Homepage, HomepageAdmin)
