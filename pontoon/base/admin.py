from __future__ import absolute_import

import uuid

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import (
    UserAdmin as AuthUserAdmin,
    GroupAdmin,
)
from django.contrib.auth.models import User, Group
from django.contrib.admin.utils import NestedObjects
from django.utils.text import capfirst
from django.utils.encoding import force_text
from django.forms.models import ModelForm
from django.forms import ChoiceField
from django.urls import reverse

from pontoon.actionlog.models import ActionLog
from pontoon.base import models
from pontoon.base import utils
from pontoon.terminology.models import Term

from pontoon.teams.utils import log_user_groups


AGGREGATED_STATS_FIELDS = (
    "total_strings",
    "approved_strings",
    "fuzzy_strings",
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

    def save_model(self, request, obj, form, change):
        """
        Save a user and log changes in its roles.
        """
        super(UserAdmin, self).save_model(request, obj, form, change)

        # Users can only be moved between groups upon editing, not creation
        if "groups" in form.cleaned_data:
            add_groups, remove_groups = utils.get_m2m_changes(
                obj.groups, form.cleaned_data["groups"]
            )

            log_user_groups(request.user, obj, (add_groups, remove_groups))

    # This method overrite the default delete process. We are creating new user with random hash
    # and updating the cascade relationships on the objects with this new user. Then actual user gets
    # deleted. By this way we persist translations, comments etc for deleted user.
    # Bug 1561663 Admin should be able to remove an account
    def delete_model(self, request, obj):
        random_hash = uuid.uuid4().hex
        new_user = User.objects.create_user(
            username="deleted-user-" + random_hash,
            email="deleted-user-" + random_hash + "@example.com",
            first_name="Deleted User",
            is_active=False,
        )

        ActionLog.objects.filter(performed_by=obj).update(performed_by=new_user)
        models.PermissionChangelog.objects.filter(performed_by=obj).update(
            performed_by=new_user
        )
        models.PermissionChangelog.objects.filter(performed_on=obj).update(
            performed_on=new_user
        )
        models.Project.objects.filter(contact=obj).update(contact=new_user)
        models.Translation.objects.filter(user=obj).update(user=new_user)
        models.Translation.objects.filter(approved_user=obj).update(
            approved_user=new_user
        )
        models.Translation.objects.filter(unapproved_user=obj).update(
            unapproved_user=new_user
        )
        models.Translation.objects.filter(rejected_user=obj).update(
            rejected_user=new_user
        )
        models.Translation.objects.filter(unrejected_user=obj).update(
            unrejected_user=new_user
        )
        Term.objects.filter(created_by=obj).update(created_by=new_user)
        models.Comment.objects.filter(author=obj).update(author=new_user)

        super(UserAdmin, self).delete_model(request, obj)

    # This method is to overrite bulk delete method from the user list page
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)

    # Due to cascade relationship, all the pontoon objects gets listed on confirmation page.
    # This method mannually filtering data which is not actualy getting deleted.
    def get_deleted_objects(self, objs, request):
        exclude_types = [
            models.Comment.__name__,
            ActionLog.__name__,
            models.PermissionChangelog.__name__,
            models.Project.__name__,
            models.Translation.__name__,
            Term.__name__,
        ]
        collector = NestedObjects(using="default")
        collector.collect(objs)

        def get_class_name_from_label(label):
            return label.split(".")[1]

        def format_callback(obj):
            opts = obj._meta
            no_edit_link = "%s: %s" % (capfirst(opts.verbose_name), force_text(obj))
            return no_edit_link

        def fun_callback(x):
            if get_class_name_from_label(x._meta.label) in exclude_types:
                return False
            return True

        items = collector.nested()
        for item in items:
            if isinstance(item, list):
                filtered_item = list(filter(lambda x: fun_callback(x), item))
                filtered_item = map(lambda x: format_callback(x), filtered_item)
                item.clear()
                item.extend(filtered_item)

        protected = []
        perms_needed = []
        model_count = {
            model._meta.verbose_name_plural: len(objs)
            for model, objs in collector.model_objs.items()
            if get_class_name_from_label(model._meta.label) not in exclude_types
        }
        return (items, model_count, perms_needed, protected)


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
            return ((name, "{} ({})".format(name, collate)) for name, collate in rows)

    def __init__(self, *args, **kwargs):
        super(LocaleAdminForm, self).__init__(*args, **kwargs)
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
        "permalink_prefix",
        "last_synced_revisions",
        "source_repo",
    )


class SubpageInline(admin.TabularInline):
    model = models.Subpage
    extra = 0
    verbose_name_plural = "Subpages"
    fields = (
        "project",
        "name",
        "url",
        "resources",
    )
    raw_id_fields = ("resources",)


class ProjectAdmin(admin.ModelAdmin):
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

    def contact_person(self, obj):
        return obj.contact.name_or_email if obj.contact else "-"

    contact_person.admin_order_field = "contact__first_name"

    def enabled(self, obj):
        return not obj.disabled

    enabled.boolean = True
    enabled.admin_order_field = "disabled"

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
                    "system_project",
                    "visibility",
                    "pretranslation_enabled",
                    "sync_disabled",
                    "disabled",
                ),
            },
        ),
        ("WEBSITE", {"fields": ("url", "width", "links")}),
    )
    readonly_fields = AGGREGATED_STATS_FIELDS + ("latest_translation",)
    inlines = (
        SubpageInline,
        ProjectLocaleInline,
        RepositoryInline,
        ExternalProjectResourceInline,
    )


class ResourceAdmin(admin.ModelAdmin):
    search_fields = ["path", "format", "project__name", "project__slug"]
    list_display = ("pk", "project", "path", "format", "deadline")


class TranslatedResourceAdmin(admin.ModelAdmin):
    search_fields = ["resource__path", "locale__name", "locale__code"]
    list_display = ("pk", "resource", "locale")
    readonly_fields = AGGREGATED_STATS_FIELDS + ("latest_translation",)
    raw_id_fields = ("resource",)


class EntityAdmin(admin.ModelAdmin):
    raw_id_fields = ("resource",)


class TranslationAdmin(admin.ModelAdmin):
    raw_id_fields = ("entity",)


class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ("translation", "entity")


class TranslationMemoryEntryAdmin(admin.ModelAdmin):
    search_fields = ["source", "target", "locale__name", "locale__code"]
    list_display = ("pk", "source", "target", "locale")
    raw_id_fields = (
        "entity",
        "translation",
    )


class ChangedEntityLocaleAdmin(admin.ModelAdmin):
    search_fields = ["entity__string", "locale__name", "locale__code"]
    # Entity column should come last, for it can be looong
    list_display = ("pk", "when", "locale", "entity")
    raw_id_fields = ("entity",)


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

    def get_user_edit_url(self, user_pk):
        return reverse(
            "admin:{}_{}_change".format(
                get_user_model()._meta.app_label, get_user_model()._meta.model_name,
            ),
            args=(user_pk,),
        )

    def performed_on_email(self, obj):
        return '<a href="{}">{}</a>'.format(
            self.get_user_edit_url(obj.performed_on_id), obj.performed_on.email
        )

    performed_on_email.short_description = "Performed on"
    performed_on_email.allow_tags = True

    def performed_by_email(self, obj):
        return '<a href="{}">{}</a>'.format(
            self.get_user_edit_url(obj.performed_by_id), obj.performed_by.email
        )

    performed_by_email.short_description = "Performed by"
    performed_by_email.allow_tags = True


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
admin.site.register(models.PermissionChangelog, UserRoleLogActionAdmin)
admin.site.register(models.Comment, CommentAdmin)
