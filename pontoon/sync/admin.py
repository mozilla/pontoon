from django.contrib import admin
from pontoon.sync import models


class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('pk', 'start_time', 'end_time', 'duration')


class ProjectSyncLogAdmin(admin.ModelAdmin):
    list_display = ('project', 'status', 'start_time', 'end_time', 'duration')


class RepositorySyncLogAdmin(admin.ModelAdmin):
    list_display = ('repository_url', 'start_time', 'end_time', 'duration')

    def repository_url(self, obj):
        return obj.repository.url


admin.site.register(models.SyncLog, SyncLogAdmin)
admin.site.register(models.ProjectSyncLog, ProjectSyncLogAdmin)
admin.site.register(models.RepositorySyncLog, RepositorySyncLogAdmin)
