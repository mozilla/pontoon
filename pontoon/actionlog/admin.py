from __future__ import absolute_import

from django.contrib import admin

from pontoon.actionlog.models import ActionLog


class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('action_type',)
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
    fieldsets = (
        (None, {
            'fields': (
                'action_type',
                'performed_by',
            ),
        }),
    )


admin.site.register(ActionLog, ActionLogAdmin)
