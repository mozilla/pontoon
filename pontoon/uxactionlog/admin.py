from django.contrib import admin

from pontoon.uxactionlog.models import UXActionLog


class UXActionLogAdmin(admin.ModelAdmin):
    search_fields = [
        "action_type",
    ]
    list_display = (
        "action_type",
        "created_at",
        "experiment",
    )


admin.site.register(UXActionLog, UXActionLogAdmin)
