# -*- coding: utf-8 -*-
"""
Django's (version 1.8.4) executes post_migration hooked in django.contrib.auth after every migration.
This particular signal creates content_types and adds object's permissions to database.
However, next migrations will require ContentTypes and some of permissions that's
why we have to create them before post_migration is called. Important fact is there's currently no way
to remove ContentType and Permissions created in this migration because they will be recreated by Django.
That's why downgrade is a noop function.
"""

from __future__ import unicode_literals

from django.db import migrations


def create_locale_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    locale_content_type, _ = ContentType.objects.get_or_create(app_label='base', model='locale')

    Permission.objects.get_or_create(codename='can_translate_locale', content_type=locale_content_type,
        name="Can add translations")
    Permission.objects.get_or_create(codename='can_manage_locale', content_type=locale_content_type,
        name="Can manage locale")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0040_auto_20151017_0005'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.RunPython(create_locale_permissions, noop)
    ]
