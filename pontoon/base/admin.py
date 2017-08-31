from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as AuthUserAdmin,
    GroupAdmin,
)
from django.contrib.auth.models import User, Group
from django.forms.models import ModelForm
from django.forms import ChoiceField

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
    exclude = ('locales_order',)
    verbose_name_plural = 'Settings'


class UserAdmin(AuthUserAdmin):
    search_fields = ['email', 'first_name']
    list_display = ('email', 'first_name', 'last_login', 'date_joined')
    list_filter = ('is_staff', 'is_superuser')
    inlines = (UserProfileInline,)


class ExternalResourceInline(admin.TabularInline):
    model = models.ExternalResource
    extra = 0
    verbose_name_plural = 'External Resources'


class ExternalLocaleResourceInline(ExternalResourceInline):
    fields = ('locale', 'name', 'url',)


class LocaleAdminForm(ModelForm):
    """
    Dynamically loads a list of available collations in your database.
    """
    db_collation = ChoiceField()

    @property
    def db_collations_choices(self):
        """
        Return all available collations in the current postgresql instance.

        More info about the management of collations in PostgreSQL:
        https://www.postgresql.org/docs/9.4/static/collation.html
        """
        # To avoid pre-mature initialization of db-context.
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT collname, collcollate  FROM pg_collation")
            rows = cursor.fetchall()
            return ((name, "{} ({})".format(name, collate)) for name, collate in rows)

    def __init__(self, *args, **kwargs):
        super(LocaleAdminForm, self).__init__(*args, **kwargs)
        self.fields['db_collation'].choices = self.db_collations_choices
        self.fields['db_collation'].help_text = self._meta.model._meta.get_field('db_collation').help_text


class LocaleAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']
    list_display = ('pk', 'name', 'code', 'script', 'direction', 'population',
                    'cldr_plurals', 'nplurals', 'plural_rule')
    exclude = ('translators_group', 'managers_group')
    readonly_fields = AGGREGATED_STATS_FIELDS + ('latest_translation',)
    inlines = (ExternalLocaleResourceInline,)
    form = LocaleAdminForm


class ExternalProjectResourceInline(ExternalResourceInline):
    fields = ('project', 'name', 'url',)


class ProjectLocaleInline(admin.TabularInline):
    model = models.ProjectLocale
    extra = 0
    verbose_name_plural = 'Locales'
    fields = ('locale',)


class RepositoryInline(admin.TabularInline):
    model = models.Repository
    extra = 0
    verbose_name_plural = 'Repositories'
    fields = ('type', 'url', 'branch', 'website', 'permalink_prefix', 'last_synced_revisions',
              'source_repo',)


class SubpageInline(admin.TabularInline):
    model = models.Subpage
    extra = 0
    verbose_name_plural = 'Subpages'
    fields = ('project', 'name', 'url', 'resources',)
    raw_id_fields = ('resources',)


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name', 'slug']
    list_display = ('name', 'slug', 'deadline', 'priority', 'contact_person', 'pk', 'enabled')
    ordering = ('disabled',)

    def contact_person(self, obj):
        return obj.contact.name_or_email if obj.contact else '-'
    contact_person.admin_order_field = 'contact__first_name'

    def enabled(self, obj):
        return not obj.disabled
    enabled.boolean = True
    enabled.admin_order_field = 'disabled'

    fieldsets = (
        (None, {
            'fields': (
                'name', 'slug', 'info', 'deadline', 'priority',
                'contact', 'langpack_url', 'can_be_requested', 'disabled'),
        }),
        ('WEBSITE', {
            'fields': ('url', 'width', 'links'),
        }),
    )
    readonly_fields = AGGREGATED_STATS_FIELDS + ('latest_translation',)
    inlines = (
        SubpageInline, ProjectLocaleInline,
        RepositoryInline, ExternalProjectResourceInline
    )


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
admin.site.register(Group, GroupAdmin)
admin.site.register(models.Locale, LocaleAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Resource, ResourceAdmin)
admin.site.register(models.TranslatedResource, TranslatedResourceAdmin)
admin.site.register(models.Entity, EntityAdmin)
admin.site.register(models.Translation, TranslationAdmin)
admin.site.register(models.TranslationMemoryEntry, TranslationMemoryEntryAdmin)
admin.site.register(models.ChangedEntityLocale, ChangedEntityLocaleAdmin)
