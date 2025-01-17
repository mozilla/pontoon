from django.contrib import admin

from pontoon.insights.models import (
    LocaleInsightsSnapshot,
    ProjectLocaleInsightsSnapshot,
)


class LocaleInsightsSnapshotAdmin(admin.ModelAdmin):
    search_fields = [
        "pk",
        "locale__code",
        "locale__name",
    ]
    list_display = (
        "pk",
        "locale",
        "created_at",
        "completion",
        "unreviewed_strings",
    )


class ProjectLocaleInsightsSnapshotAdmin(admin.ModelAdmin):
    search_fields = [
        "pk",
        "project_locale__project__name",
        "project_locale__project__slug",
        "project_locale__locale__code",
        "project_locale__locale__name",
    ]
    list_display = (
        "pk",
        "project_locale",
        "created_at",
        "completion",
        "unreviewed_strings",
    )
    readonly_fields = ("project_locale",)


admin.site.register(LocaleInsightsSnapshot, LocaleInsightsSnapshotAdmin)
admin.site.register(ProjectLocaleInsightsSnapshot, ProjectLocaleInsightsSnapshotAdmin)
