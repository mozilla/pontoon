from django.contrib import admin

from pontoon.insights.models import LocaleInsightsSnapshot


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


admin.site.register(LocaleInsightsSnapshot, LocaleInsightsSnapshotAdmin)
