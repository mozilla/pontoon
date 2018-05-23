from django.contrib import admin
from pontoon.checks import models


class FailedCheckModelAdmin(admin.ModelAdmin):
    search_fields = ['message']
    list_display = (
        'project',
        'locale',
        'resource',
        'translation',
        'message',
    )

    def project(self, obj):
        return obj.translation.entity.resource.project.name

    def locale(self, obj):
        return obj.translation.locale.code

    def resource(self, obj):
        return obj.translation.entity.resource.path

    def translation(self, obj):
        return obj.translation.string


class WarningAdmin(FailedCheckModelAdmin):
    pass


class ErrorAdmin(FailedCheckModelAdmin):
    pass


admin.site.register(models.Warning, WarningAdmin)
admin.site.register(models.Error, ErrorAdmin)
