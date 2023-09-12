import csv
import uuid

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User
from django.forms import ChoiceField
from django.forms.models import ModelForm
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from guardian.admin import GuardedModelAdmin

from pontoon.actionlog.models import ActionLog
from pontoon.base import models, utils
from pontoon.teams.utils import log_user_groups
from pontoon.terminology.models import Term


AGGREGATED_STATS_FIELDS = (
    "approved_strings",
    "pretranslated_strings",
    "strings_with_errors",
    "strings_with_warnings",
    "unreviewed_strings",
)


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    max_num = 1
    can_delete = False
    exclude = ("locales_order",)
    verbose_name_plural = "Settings"


class UserAdmin(AuthUserAdmin):
    search_fields = ["email", "first_name"]
    list_display = ("email", "first_name", "last_login", "date_joined")
    list_filter = ("is_staff", "is_superuser")
    inlines = (UserProfileInline,)

    add_fieldsets = (
        (
            None,
            {
                "classes": "wide",
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """
        Save a user and log changes in its roles.
        """
        super().save_model(request, obj, form, change)

        # Users can only be moved between groups upon editing, not creation
        if "groups" in form.cleaned_data:
            add_groups, remove_groups = utils.get_m2m_changes(
                obj.groups, form.cleaned_data["groups"]
            )

            log_user_groups(request.user, obj, (add_groups, remove_groups))

    # Before deleting the user, we need to make sure data we care about is kept,
    # especially translations the user authored. Hence we create a new anonymized user,
    # move user data we care about to it and then delete the user.
    # See bug 1561663 for details.
    def delete_model(self, request, obj):
        random_hash = uuid.uuid4().hex
        new_user = User.objects.create_user(
            username="deleted-user-" + random_hash,
            email="deleted-user-" + random_hash + "@example.com",
            first_name="Deleted User",
            is_active=False,
        )

        ActionLog.objects.filter(performed_by=obj).update(performed_by=new_user)
        models.PermissionChangelog.objects.filter(performed_by=obj).update(performed_by=new_user)
        models.PermissionChangelog.objects.filter(performed_on=obj).update(performed_on=new_user)
        models.Project.objects.filter(contact=obj).update(contact=new_user)
        models.Translation.objects.filter(user=obj).update(user=new_user)
        models.Translation.objects.filter(approved_user=obj).update(approved_user=new_user)
        models.Translation.objects.filter(unapproved_user=obj).update(unapproved_user=new_user)
        models.Translation.objects.filter(rejected_user=obj).update(rejected_user=new_user)
        models.Translation.objects.filter(unrejected_user=obj).update(unrejected_user=new_user)
        Term.objects.filter(created_by=obj).update(created_by=new_user)
        models.Comment.objects.filter(author=obj).update(author=new_user)

        super().delete_model(request, obj)

    # This method is to override bulk delete method from the user list page
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)


class ExternalResourceInline(admin.TabularInline):
    model = models.ExternalResource
    extra = 0
    verbose_name_plural = "External Resources"


class ExternalLocaleResourceInline(ExternalResourceInline):
    fields = (
        "locale",
        "name",
        "url",
    )


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
            return ((name, f"{name} ({collate})") for name, collate in rows)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["db_collation"].choices = self.db_collations_choices
        self.fields["db_collation"].help_text = self._meta.model._meta.get_field(
            "db_collation"
        ).help_text


class LocaleAdmin(admin.ModelAdmin):
    search_fields = ["name", "code"]
    list_display = (
        "pk",
        "name",
        "code",
        "script",
        "direction",
        "population",
        "cldr_plurals",
        "nplurals",
        "plural_rule",
    )
    exclude = ("translators_group", "managers_group")
    readonly_fields = AGGREGATED_STATS_FIELDS + ("latest_translation",)
    inlines = (ExternalLocaleResourceInline,)
    form = LocaleAdminForm


class ExternalProjectResourceInline(ExternalResourceInline):
    fields = (
        "project",
        "name",
        "url",
    )


class ProjectLocaleInline(admin.TabularInline):
    model = models.ProjectLocale
    extra = 0
    verbose_name_plural = "Locales"
    fields = (
        "locale",
        "readonly",
        "pretranslation_enabled",
        "has_custom_translators",
    )


class RepositoryInline(admin.TabularInline):
    model = models.Repository
    extra = 0
    verbose_name_plural = "Repositories"
    fields = (
        "type",
        "url",
        "branch",
        "website",
        "last_synced_revisions",
        "source_repo",
    )


class ProjectAdmin(GuardedModelAdmin):
    search_fields = ["name", "slug"]
    list_display = (
        "name",
        "slug",
        "deadline",
        "priority",
        "contact_person",
        "pk",
        "system_project",
        "visibility",
        "pretranslation_enabled",
        "sync_disabled",
        "enabled",
    )
    ordering = ("disabled",)
    autocomplete_fields = ["contact"]

    @admin.display(ordering="contact__first_name")
    def contact_person(self, obj):
        return obj.contact.name_or_email if obj.contact else "-"

    @admin.display(boolean=True, ordering="disabled")
    def enabled(self, obj):
        return not obj.disabled

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "info",
                    "deadline",
                    "priority",
                    "contact",
                    "langpack_url",
                    "configuration_file",
                    "can_be_requested",
                    "date_created",
                    "date_disabled",
                    "date_modified",
                    "system_project",
                    "visibility",
                    "pretranslation_enabled",
                    "sync_disabled",
                    "disabled",
                ),
            },
        ),
    )
    readonly_fields = AGGREGATED_STATS_FIELDS + ("latest_translation",)
    inlines = (
        ProjectLocaleInline,
        RepositoryInline,
        ExternalProjectResourceInline,
    )

    actions = ["export_project_translation_stats_to_CSV"]

    @admin.action(description="Export translations and stats to CSV")
    def export_project_translation_stats_to_CSV(self, request, queryset):
        """
        Export untranslated strings to CSV.
        """

        if queryset.count() != 1:
            self.message_user(
                request,
                "Please select one and only one project to export.",
                level=messages.ERROR,
            )
            return
        p = queryset.first()
        project_locales = p.project_locale.all()
        pl_names = [ pl.locale.name for pl in project_locales ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{p.slug}_approved_translations_or_stats.csv"'

        headers = ['Project', 'Resource', "Source Strings"] + pl_names
        writer = csv.writer(response,  quoting=csv.QUOTE_ALL)
        writer.writerow(headers)

        csv_dict = { field: [] for field in headers}
        for resource in p.resources.all():
            all_resource_entities = resource.entities.all()
            for i, pl in enumerate(project_locales):
                # l = pl.locale
                # q = Q(Q(resource__project__id=p.id) & Q(resource__id=resource.id) & ~Entity.objects.translated(l, p))
                # untranslated_entities = Entity.objects.filter(q)
                if i == 0:
                    csv_dict['Project'] += [ p.name ] * len(all_resource_entities)
                    csv_dict['Resource'] += [ resource.path ] * len(all_resource_entities)
                for entity in all_resource_entities:
                    if i == 0:
                        csv_dict['Source Strings'].append(entity.string)
                    if translation := entity.translation_set.filter(active=True, locale_id=pl.locale.id).first():
                        if translation.approved:
                            mark = translation.string
                        elif translation.pretranslated:
                            mark = 'PRETRANSLATED'
                        elif translation.rejected:
                            mark = 'REJECTED'
                        elif translation.fuzzy:
                            mark = 'FUZZY'
                        else:
                            mark = 'UNREVIEWED'
                    else:
                        mark = 'MISSING'
                    csv_dict[pl.locale.name].append(mark)
        
        columns = [ column for column in csv_dict.values() ]
        rows = list(zip(*columns))
        writer.writerows(rows)

        self.message_user(
            request,
            "CSV file generated.",
            level=messages.INFO,
        )
        return response



class ProjectLocaleAdmin(GuardedModelAdmin):
    search_fields = ["project__name", "project__slug", "locale__name", "locale__code"]
    list_display = ("pk", "project", "locale", "readonly", "pretranslation_enabled", "has_custom_translators")
    ordering = ("-pk",)
    actions = ["enable_custom_translators"]
    
    @admin.action(description="Enable custom translators")
    def enable_custom_translators(self, request, queryset):
        for project_locale in queryset:
            project_locale.has_custom_translators = True
            project_locale.save()
            self.message_user(
                request,
                f"Project Locale has been enabled to have custom translators: {project_locale.__str__()}",
                level=messages.INFO,
            )

class ResourceAdmin(admin.ModelAdmin):
    search_fields = ["path", "format", "project__name", "project__slug"]
    list_display = ("pk", "project", "path", "format", "deadline")


class TranslatedResourceAdmin(admin.ModelAdmin):
    search_fields = ["resource__path", "locale__name", "locale__code"]
    list_display = ("pk", "resource", "locale")
    readonly_fields = AGGREGATED_STATS_FIELDS + ("latest_translation",)
    autocomplete_fields = ("resource",)


class EntityAdmin(admin.ModelAdmin):
    search_fields = ["string"]
    autocomplete_fields = ("resource",)


class TranslationAdmin(admin.ModelAdmin):
    search_fields = ["string"]
    autocomplete_fields = [
        "entity",
        "user",
        "approved_user",
        "unapproved_user",
        "rejected_user",
        "unrejected_user",
    ]


class ProjectSlugHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)


class LocaleCodeHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)


class CommentAdmin(admin.ModelAdmin):
    search_fields = ["content"]
    autocomplete_fields = ("author", "translation", "entity")


class TranslationMemoryEntryAdmin(admin.ModelAdmin):
    search_fields = ["source", "target", "locale__name", "locale__code"]
    list_display = ("pk", "source", "target", "locale")
    autocomplete_fields = (
        "entity",
        "translation",
    )


class ChangedEntityLocaleAdmin(admin.ModelAdmin):
    search_fields = ["entity__string", "locale__name", "locale__code"]
    # Entity column should come last, for it can be looong
    list_display = ("pk", "when", "locale", "entity")
    autocomplete_fields = ("entity",)


class UserRoleLogActionAdmin(admin.ModelAdmin):
    search_fields = (
        "performed_by__email",
        "performed_on__email",
        "group__name",
        "created_at",
    )
    list_display = (
        "performed_by_email",
        "action_type",
        "performed_on_email",
        "group",
        "created_at",
    )
    ordering = ("-created_at",)
    autocomplete_fields = (
        "performed_by",
        "performed_on",
        "group",
    )

    def get_user_edit_url(self, user_pk):
        return reverse(
            "admin:{}_{}_change".format(
                get_user_model()._meta.app_label,
                get_user_model()._meta.model_name,
            ),
            args=(user_pk,),
        )

    @admin.display(description="Performed on")
    def performed_on_email(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            self.get_user_edit_url(obj.performed_on_id),
            obj.performed_on.email,
        )

    @admin.display(description="Performed by")
    def performed_by_email(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            self.get_user_edit_url(obj.performed_by_id),
            obj.performed_by.email,
        )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(models.Locale, LocaleAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.ProjectLocale, ProjectLocaleAdmin)
admin.site.register(models.Resource, ResourceAdmin)
admin.site.register(models.TranslatedResource, TranslatedResourceAdmin)
admin.site.register(models.Entity, EntityAdmin)
admin.site.register(models.Translation, TranslationAdmin)
admin.site.register(models.TranslationMemoryEntry, TranslationMemoryEntryAdmin)
admin.site.register(models.ChangedEntityLocale, ChangedEntityLocaleAdmin)
admin.site.register(models.PermissionChangelog, UserRoleLogActionAdmin)
admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.ProjectSlugHistory, ProjectSlugHistoryAdmin)
admin.site.register(models.LocaleCodeHistory, LocaleCodeHistoryAdmin)
