from django.contrib import admin

from pontoon.messaging import models


class MessageAdmin(admin.ModelAdmin):
    list_display = ("pk", "sent_at", "sender", "subject", "body")
    autocomplete_fields = ["sender", "recipients"]


admin.site.register(models.Message, MessageAdmin)
