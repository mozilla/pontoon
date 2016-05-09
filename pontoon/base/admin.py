from django.contrib import admin
from django.contrib.auth.models import User, Group
from pontoon.base import models


class UserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'first_name']
    list_display = ('email', 'first_name', 'last_login', 'date_joined')
    list_filter = ('is_staff', 'is_superuser')


class LocaleAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']
    list_display = ('pk', 'name', 'code', 'nplurals', 'plural_rule', 'cldr_plurals')


class ProjectLocaleAdmin(admin.ModelAdmin):
    search_fields = ['project__name', 'project__slug', 'locale__name', 'locale__code']
    list_display = ('pk', 'project', 'locale')


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name', 'slug']
    list_display = ('pk', 'name', 'slug', 'url', 'disabled', 'has_changed')


class RepositoryAdmin(admin.ModelAdmin):
    search_fields = ['url', 'permalink_prefix', 'project__name', 'project__slug']
    list_display = ('pk', 'project', 'type', 'url', 'permalink_prefix')


class SubpageAdmin(admin.ModelAdmin):
    search_fields = ['name', 'url', 'project__name', 'project__slug']
    list_display = ('pk', 'project', 'name', 'url')


class ResourceAdmin(admin.ModelAdmin):
    search_fields = ['path', 'format', 'project__name', 'project__slug']
    list_display = ('pk', 'project', 'path', 'format')


class TranslatedResourceAdmin(admin.ModelAdmin):
    search_fields = ['resource__path', 'locale__name', 'locale__code']
    list_display = ('pk', 'resource', 'locale')


class TranslationMemoryEntryAdmin(admin.ModelAdmin):
    search_fields = ['source', 'target', 'locale__name', 'locale__code']
    list_display = ('pk', 'source', 'target', 'locale')


class ChangedEntityLocaleAdmin(admin.ModelAdmin):
    search_fields = ['entity__string', 'locale__name', 'locale__code']
    # Entity column should come last, for it can be looong
    list_display = ('pk', 'when', 'locale', 'entity')


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'user__first_name']
    list_display = ('pk', 'user_email', 'quality_checks', 'force_suggestions')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'


admin.site.register(Group)
admin.site.register(User, UserAdmin)

admin.site.register(models.Locale, LocaleAdmin)
admin.site.register(models.ProjectLocale, ProjectLocaleAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Repository, RepositoryAdmin)
admin.site.register(models.Subpage, SubpageAdmin)
admin.site.register(models.Resource, ResourceAdmin)
admin.site.register(models.TranslatedResource, TranslatedResourceAdmin)
admin.site.register(models.Entity)
admin.site.register(models.Translation)
admin.site.register(models.TranslationMemoryEntry, TranslationMemoryEntryAdmin)
admin.site.register(models.ChangedEntityLocale, ChangedEntityLocaleAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
