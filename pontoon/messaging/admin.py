from django.contrib import admin

from pontoon.messaging import forms, models


class MessageAdmin(admin.ModelAdmin):
    list_display = ("pk", "sent_at", "sender", "subject", "body")
    autocomplete_fields = ["sender", "recipients"]


class EmailContentAdmin(admin.ModelAdmin):
    list_display = ("email", "subject", "created_at", "updated_at")
    form = forms.EmailContentForm


admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.EmailContent, EmailContentAdmin)
