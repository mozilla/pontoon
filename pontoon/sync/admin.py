from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from pontoon.sync import models


TIMES = ("start_time", "end_time", "duration")


class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        url = reverse(
            "admin:%s_%s_change"
            % (instance._meta.app_label, instance._meta.model_name),
            args=[instance.pk],
        )
        if instance.pk:
            return mark_safe(u'<a href="{u}">edit</a>'.format(u=url))
        else:
            return ""


class ProjectSyncLogInline(EditLinkToInlineObject, admin.TabularInline):
    model = models.ProjectSyncLog
    extra = 0
    verbose_name_plural = "Projects"
    readonly_fields = ("edit_link",)


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

    def repository_url(self, obj):
        return obj.repository.url


admin.site.register(models.SyncLog, SyncLogAdmin)
admin.site.register(models.ProjectSyncLog, ProjectSyncLogAdmin)
admin.site.register(models.RepositorySyncLog, RepositorySyncLogAdmin)
