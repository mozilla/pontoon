from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User

from pontoon.base import models


AGGREGATED_STATS_FIELDS = (
    'total_strings',
    'approved_strings',
    'translated_strings',
    'fuzzy_strings',
)


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    max_num = 1
    can_delete = False
    fields = ('quality_checks', 'force_suggestions',)
    verbose_name_plural = 'Settings'


class UserAdmin(AuthUserAdmin):
    search_fields = ['email', 'first_name']
    list_display = ('email', 'first_name', 'last_login', 'date_joined')
    list_filter = ('is_staff', 'is_superuser')
    inlines = (UserProfileInline,)


class LocaleAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']
    list_display = ('pk', 'name', 'code', 'nplurals', 'plural_rule', 'cldr_plurals')
    exclude = ('translators_group', 'managers_group')
    readonly_fields = AGGREGATED_STATS_FIELDS + ('latest_translation',)


class ProjectLocaleInline(admin.TabularInline):
    model = models.ProjectLocale
    extra = 0
    verbose_name_plural = 'Locales'
    fields = ('locale',)


class RepositoryInline(admin.TabularInline):
    model = models.Repository
    extra = 0
    verbose_name_plural = 'Repositories'
    fields = ('type', 'url', 'branch', 'permalink_prefix', 'last_synced_revisions', 'source_repo',)


class SubpageInline(admin.TabularInline):
    model = models.Subpage
    extra = 0
    verbose_name_plural = 'Subpages'
    fields = ('project', 'name', 'url', 'resources',)
    raw_id_fields = ('resources',)


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name', 'slug']
    list_display = ('name', 'slug', 'pk', 'disabled')

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'info_brief', 'langpack_url', 'disabled',),
        }),
        ('WEBSITE', {
            'fields': ('url', 'width', 'links'),
        }),
    )
    readonly_fields = AGGREGATED_STATS_FIELDS + ('latest_translation',)
    inlines = (ProjectLocaleInline, RepositoryInline, SubpageInline)


class ResourceAdmin(admin.ModelAdmin):
    search_fields = ['path', 'format', 'project__name', 'project__slug']
    list_display = ('pk', 'project', 'path', 'format')


class TranslatedResourceAdmin(admin.ModelAdmin):
    search_fields = ['resource__path', 'locale__name', 'locale__code']
    list_display = ('pk', 'resource', 'locale')
    readonly_fields = AGGREGATED_STATS_FIELDS + ('latest_translation',)
    raw_id_fields = ('resource',)


class EntityAdmin(admin.ModelAdmin):
    raw_id_fields = ('resource',)


class TranslationAdmin(admin.ModelAdmin):
    raw_id_fields = ('entity',)


class TranslationMemoryEntryAdmin(admin.ModelAdmin):
    search_fields = ['source', 'target', 'locale__name', 'locale__code']
    list_display = ('pk', 'source', 'target', 'locale')
    raw_id_fields = ('entity', 'translation',)


class ChangedEntityLocaleAdmin(admin.ModelAdmin):
    search_fields = ['entity__string', 'locale__name', 'locale__code']
    # Entity column should come last, for it can be looong
    list_display = ('pk', 'when', 'locale', 'entity')
    raw_id_fields = ('entity',)


admin.site.register(User, UserAdmin)
admin.site.register(models.Locale, LocaleAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Resource, ResourceAdmin)
admin.site.register(models.TranslatedResource, TranslatedResourceAdmin)
admin.site.register(models.Entity, EntityAdmin)
admin.site.register(models.Translation, TranslationAdmin)
admin.site.register(models.TranslationMemoryEntry, TranslationMemoryEntryAdmin)
admin.site.register(models.ChangedEntityLocale, ChangedEntityLocaleAdmin)
