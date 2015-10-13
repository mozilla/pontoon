# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def remove_deleted_migrations(apps, schema_editor):
    Translation = apps.get_model('base', 'Translation')
    for t in Translation.objects.filter(deleted__isnull=False):
        t.delete()


def noop(apps, schema_editor):
    pass  # Nothing to do on the trip backwards.


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0033_remove_repository_multi_locale'),
    ]

    operations = [
        migrations.RunPython(remove_deleted_migrations, noop)
    ]
