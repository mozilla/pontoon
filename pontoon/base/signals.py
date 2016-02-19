from guardian.models import GroupObjectPermission

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver

from pontoon.base import errors
from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    TranslatedResource,
    UserProfile,
)


@receiver(post_save, sender=ProjectLocale)
def project_locale_added(sender, **kwargs):
    """
    When a new locale is added to a project, mark the project as
    changed.
    """
    created = kwargs.get('created', False)
    raw = kwargs.get('raw', False)
    project_locale = kwargs.get('instance', None)
    if created and not raw and project_locale is not None:
        project = project_locale.project
        project.has_changed = True
        project.save(update_fields=['has_changed'])


@receiver(post_delete, sender=ProjectLocale)
def project_locale_removed(sender, **kwargs):
    """
    When locale is removed from a project, delete TranslatedResources
    and aggregate project and locale stats.
    """
    project_locale = kwargs.get('instance', None)
    if project_locale is not None:
        project = project_locale.project
        locale = project_locale.locale

        TranslatedResource.objects.filter(resource__project=project, locale=locale).delete()
        project.aggregate_stats()
        locale.aggregate_stats()


@receiver(pre_delete, sender=Locale)
def locale_deleted(sender, **kwargs):
    """
    Before locale is deleted, aggregate stats for all locale projects.
    """
    locale = kwargs.get('instance', None)
    if locale is not None:
        for project in locale.project_set.all():
            project.aggregate_stats()


@receiver(pre_delete, sender=Project)
def project_deleted(sender, **kwargs):
    """
    Before project is deleted, aggregate stats for all project locales.
    """
    project = kwargs.get('instance', None)
    if project is not None:
        for locale in project.locales.all():
            locale.aggregate_stats()


@receiver(pre_save, sender=Locale)
def create_locale_translators_group(sender, **kwargs):
    """
    Creates respective translators group in django's permission system.
    Managers should be able to translate and manage locale.
    """
    instance = kwargs['instance']

    if kwargs['raw'] or instance.translators_group is not None:
        return

    try:
        locale_ct = ContentType.objects.get(app_label='base', model='locale')
        locale_group, _ = Group.objects.get_or_create(name='{} translators'.format(instance.code))
        can_translate = Permission.objects.get(content_type=locale_ct, codename='can_translate_locale')
        locale_group.permissions.add(can_translate)
        instance.translators_group = locale_group
    except ObjectDoesNotExist as e:
        errors.send_exception(e)


@receiver(pre_save, sender=Locale)
def create_locale_managers_group(sender, **kwargs):
    """
    Creates respective managers group in django's permission system.
    Managers should be able to translate and manage locale.
    """
    instance = kwargs['instance']

    if kwargs['raw'] or instance.managers_group is not None:
        return

    try:
        locale_ct = ContentType.objects.get(app_label='base', model='locale')
        locale_group, _ = Group.objects.get_or_create(name='{} managers'.format(instance.code))
        can_translate = Permission.objects.get(content_type=locale_ct, codename='can_translate_locale')
        can_manage = Permission.objects.get(content_type=locale_ct, codename='can_manage_locale')
        locale_group.permissions.add(can_translate)
        locale_group.permissions.add(can_manage)
        instance.managers_group = locale_group
    except ObjectDoesNotExist as e:
        errors.send_exception(e)


@receiver(post_save, sender=Locale)
def assign_group_permissions(sender, **kwargs):
    """"
    After creation of locale, we have to assign translation and management
    permissions to groups of translators and managers assigned to locale.
    """
    if kwargs['raw'] or not kwargs['created']:
        return

    instance = kwargs['instance']

    try:
        locale_ct = ContentType.objects.get(app_label='base', model='locale')
        can_translate = Permission.objects.get(content_type=locale_ct, codename='can_translate_locale')
        can_manage = Permission.objects.get(content_type=locale_ct, codename='can_manage_locale')

        GroupObjectPermission.objects.get_or_create(object_pk=instance.pk,
            content_type=locale_ct,
            group=instance.translators_group,
            permission=can_translate)

        GroupObjectPermission.objects.get_or_create(object_pk=instance.pk,
            content_type=locale_ct,
            group=instance.managers_group,
            permission=can_translate)

        GroupObjectPermission.objects.get_or_create(object_pk=instance.pk,
            content_type=locale_ct,
            group=instance.managers_group,
            permission=can_manage)
    except ObjectDoesNotExist as e:
        errors.send_exception(e)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
