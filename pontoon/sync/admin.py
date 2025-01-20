from django.contrib import admin

from pontoon.sync.models import Sync


class SyncAdmin(admin.ModelAdmin):
    search_fields = ("project__slug",)
    list_display = ("project", "status", "start_time", "end_time", "error")


admin.site.register(Sync, SyncAdmin)
