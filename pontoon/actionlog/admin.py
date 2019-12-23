from __future__ import absolute_import

from django.contrib import admin

from pontoon.actionlog.models import ActionLog


class ActionLogAdmin(admin.ModelAdmin):
    search_fields = [
        'action_type',
    ]
    list_display = (
        'pk',
        'action_type',
        'created_at',
        'performed_by',
        'translation_id',
        'entity_id',
        'locale_id',
    )


admin.site.register(ActionLog, ActionLogAdmin)
