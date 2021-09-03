from django.contrib import admin
from pontoon.checks import models


class FailedCheckModelAdmin(admin.ModelAdmin):
    search_fields = ["message", "library"]
    raw_id_fields = ("translation",)

    list_display = (
        "translation",
        "message",
        "library",
        "locale",
        "project",
        "resource",
    )

    @admin.display
    def project(self, obj):
        return obj.translation.entity.resource.project.name

    @admin.display
    def locale(self, obj):
        return obj.translation.locale.code

    @admin.display
    def resource(self, obj):
        return obj.translation.entity.resource.path

    @admin.display
    def translation(self, obj):
        return obj.translation.string


class WarningAdmin(FailedCheckModelAdmin):
    pass


class ErrorAdmin(FailedCheckModelAdmin):
    pass


admin.site.register(models.Warning, WarningAdmin)
admin.site.register(models.Error, ErrorAdmin)
