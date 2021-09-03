from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from pontoon.sync import models


TIMES = ("start_time", "end_time", "duration")


class ProjectSyncLogInline(admin.TabularInline):
    model = models.ProjectSyncLog
    extra = 0
    verbose_name_plural = "Projects"
    readonly_fields = ("edit_link",)

    @admin.display
    def edit_link(self, obj):
        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.pk],
        )
        if obj.pk:
            return format_html('<a href="{}">edit</a>', url)
        else:
            return ""


class SyncLogAdmin(admin.ModelAdmin):
    list_display = TIMES
    inlines = (ProjectSyncLogInline,)


class RepositorySyncLogInline(admin.TabularInline):
    model = models.RepositorySyncLog
    extra = 0
    verbose_name_plural = "Repositories"


class ProjectSyncLogAdmin(admin.ModelAdmin):
    list_display = ("project", "status",) + TIMES
    inlines = (RepositorySyncLogInline,)


class RepositorySyncLogAdmin(admin.ModelAdmin):
    list_display = ("repository_url",) + TIMES

    @admin.display
    def repository_url(self, obj):
        return obj.repository.url


admin.site.register(models.SyncLog, SyncLogAdmin)
admin.site.register(models.ProjectSyncLog, ProjectSyncLogAdmin)
admin.site.register(models.RepositorySyncLog, RepositorySyncLogAdmin)
