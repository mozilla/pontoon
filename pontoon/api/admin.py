from django.contrib import admin

from .models import PersonalAccessToken


class PersonalAccessTokenAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "user__username",
        "user__email",
    )
    list_display = (
        "name",
        "user",
        "expires_at",
        "revoked",
        "created_at",
        "last_used",
    )
    list_filter = (
        "revoked",
        "expires_at",
        "created_at",
    )
    ordering = ("-created_at",)
    readonly_fields = ("token_hash", "created_at", "last_used")


admin.site.register(PersonalAccessToken, PersonalAccessTokenAdmin)
