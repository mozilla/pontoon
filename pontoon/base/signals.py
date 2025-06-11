from guardian.models import GroupObjectPermission

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from pontoon.base import errors
from pontoon.base.models import (
    Locale,
    LocaleCodeHistory,
    Project,
    ProjectLocale,
    ProjectSlugHistory,
    TranslatedResource,
    UserProfile,
)
from pontoon.messaging.emails import send_onboarding_email_1


@receiver(post_delete, sender=ProjectLocale)
def project_locale_removed(sender, **kwargs):
    project_locale = kwargs.get("instance", None)
    if project_locale is not None:
        TranslatedResource.objects.filter(
            resource__project=project_locale.project, locale=project_locale.locale
        ).delete()


def create_group(instance, group_name, perms, name_prefix):
    """
    Create all objects related to a group of users, e.g. translators, managers.
    """
    ct = ContentType.objects.get(
        app_label="base", model=instance.__class__.__name__.lower()
    )
    group, _ = Group.objects.get_or_create(name=f"{name_prefix} {group_name}")

    for perm_name in perms:
        perm = Permission.objects.get(content_type=ct, codename=perm_name)
        group.permissions.add(perm)

        setattr(instance, f"{group_name}_group", group)


def assign_group_permissions(instance, group_name, perms):
    """
    Create group object permissions.
    """
    ct = ContentType.objects.get(
        app_label="base", model=instance.__class__.__name__.lower()
    )

    for perm_name in perms:
        perm = Permission.objects.get(content_type=ct, codename=perm_name)
        group = getattr(instance, f"{group_name}_group")
        GroupObjectPermission.objects.get_or_create(
            object_pk=instance.pk, content_type=ct, group=group, permission=perm
        )


@receiver(pre_save, sender=Locale)
def create_locale_permissions_groups(sender, **kwargs):
    """
    Creates translators and managers groups for a given Locale.
    """
    instance = kwargs["instance"]

    if kwargs["raw"] or instance.managers_group is not None:
        return

    try:
        create_group(instance, "translators", ["can_translate_locale"], instance.code)
        create_group(
            instance,
            "managers",
            ["can_translate_locale", "can_manage_locale"],
            instance.code,
        )
    except ObjectDoesNotExist as e:
        errors.send_exception(e)


@receiver(pre_save, sender=ProjectLocale)
def create_project_locale_permissions_groups(sender, **kwargs):
    """
    Creates translators group for a given ProjectLocale.
    """
    instance = kwargs["instance"]

    if kwargs["raw"] or instance.translators_group is not None:
        return

    try:
        create_group(
            instance,
            "translators",
            ["can_translate_project_locale"],
            f"{instance.project.slug}/{instance.locale.code}",
        )
    except ObjectDoesNotExist as e:
        errors.send_exception(e)


@receiver(pre_save, sender=Project)
def set_project_date_modified(sender, instance, update_fields, **kwargs):
    if not instance.pk:
        return
    try:
        prev = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    for attr in [
        "configuration_file",
        "data_source",
        "disabled",
        "sync_disabled",
        "system_project",
    ]:
        if getattr(prev, attr, None) != getattr(instance, attr, None):
            instance.date_modified = timezone.now()
            if update_fields is not None and "date_modified" not in update_fields:
                update_fields.append("date_modified")
            return


@receiver(pre_save, sender=ProjectLocale)
def set_project_date_modified_locales(sender, instance, **kwargs):
    if instance.pk:
        # update
        try:
            prev = sender.objects.get(pk=instance.pk)
            if (
                prev.readonly != instance.readonly
                or prev.pretranslation_enabled != instance.pretranslation_enabled
            ):
                instance.project.date_modified = timezone.now()
                instance.project.save(update_fields=["date_modified"])
        except sender.DoesNotExist:
            pass
    elif instance.project:
        # create
        instance.project.date_modified = timezone.now()
        instance.project.save(update_fields=["date_modified"])


@receiver(post_save, sender=Locale)
def assign_locale_group_permissions(sender, **kwargs):
    """
    After creation of locale, we have to assign translation and management
    permissions to groups of translators and managers assigned to locale.
    """
    if kwargs["raw"] or not kwargs["created"]:
        return

    instance = kwargs["instance"]

    try:
        assign_group_permissions(instance, "translators", ["can_translate_locale"])
        assign_group_permissions(
            instance, "managers", ["can_translate_locale", "can_manage_locale"]
        )
    except ObjectDoesNotExist as e:
        errors.send_exception(e)


@receiver(post_save, sender=Locale)
def add_locale_to_system_projects(sender, instance, created, **kwargs):
    """
    Enable system projects for newly added locales.
    """
    if created:
        projects = Project.objects.filter(system_project=True)
        for project in projects:
            ProjectLocale.objects.create(project=project, locale=instance)
            for resource in project.resources.all():
                translated_resource = TranslatedResource.objects.create(
                    resource=resource,
                    locale=instance,
                )
                translated_resource.calculate_stats()


@receiver(post_save, sender=Locale)
def add_locale_to_terminology_project(sender, instance, created, **kwargs):
    """
    Enable Terminology project for newly added locales.
    """
    if created:
        project = Project.objects.get(slug="terminology")
        ProjectLocale.objects.create(project=project, locale=instance)
        for resource in project.resources.all():
            translated_resource = TranslatedResource.objects.create(
                resource=resource,
                locale=instance,
            )
            translated_resource.calculate_stats()


@receiver(post_save, sender=ProjectLocale)
def assign_project_locale_group_permissions(sender, **kwargs):
    """
    Assign permissions group to a given ProjectLocale.
    """
    if kwargs["raw"] or not kwargs["created"]:
        return

    instance = kwargs["instance"]

    try:
        assign_group_permissions(
            instance, "translators", ["can_translate_project_locale"]
        )
    except ObjectDoesNotExist as e:
        errors.send_exception(e)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_onboarding_email_1(instance)


@receiver(pre_save, sender=Project)
def create_slug_history(sender, instance, **kwargs):
    """
    Signal receiver that, prior to saving a Project instance, creates a ProjectSlugHistory object if the project's slug has changed.
    """
    if instance.pk:  # checks if instance is not a new object
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.slug != instance.slug:
                ProjectSlugHistory.objects.create(
                    project=instance, old_slug=old_instance.slug
                )
        except sender.DoesNotExist:
            pass


@receiver(pre_save, sender=Locale)
def create_locale_code_history(sender, instance, **kwargs):
    """
    Signal receiver that, prior to saving a Locale instance, creates a LocaleCodeHistory object if a locale's code has changed.
    """
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.code != instance.code:
                LocaleCodeHistory.objects.create(
                    locale=instance, old_code=old_instance.code
                )
        except sender.DoesNotExist:
            pass
