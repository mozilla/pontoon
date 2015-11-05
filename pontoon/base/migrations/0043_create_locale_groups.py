# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_locale_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    Locale = apps.get_model('base', 'Locale')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    GroupObjectPermission = apps.get_model('guardian', 'GroupObjectPermission')

    locale_content_type = ContentType.objects.get(app_label='base', model='locale') 
    can_translate = Permission.objects.get(content_type=locale_content_type, codename='can_translate_locale')
    can_manage = Permission.objects.get(content_type=locale_content_type, codename='can_manage_locale')

    # Create translators groups
    for locale in Locale.objects.all():
        translators_group = Group.objects.create(name='{} translators'.format(locale.code))
        translators_group.permissions.add(can_translate)
        GroupObjectPermission.objects.create(object_pk=locale.pk,
            content_type=locale_content_type,
            group=translators_group,
            permission=can_translate)

        managers_group = Group.objects.create(name='{} managers'.format(locale.code))
        managers_group.permissions.add(can_translate)
        GroupObjectPermission.objects.create(object_pk=locale.pk,
            content_type=locale_content_type,
            group=managers_group,
            permission=can_translate)

        managers_group.permissions.add(can_manage)
        GroupObjectPermission.objects.create(object_pk=locale.pk,
            content_type=locale_content_type,
            group=managers_group,
            permission=can_manage)

        locale.translators_group = translators_group
        locale.managers_group = managers_group

        locale.save()


def remove_locale_groups(apps, schema_editor):
    Locale = apps.get_model('base', 'Locale')
    Group = apps.get_model('auth', 'Group')

    Locale.objects.update(translators_group=None)
    Locale.objects.update(managers_group=None)

    Group.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0042_locale_groups'),
        ('guardian', '__first__'),
    ]

    operations = [
        migrations.RunPython(create_locale_groups, remove_locale_groups),
    ]
