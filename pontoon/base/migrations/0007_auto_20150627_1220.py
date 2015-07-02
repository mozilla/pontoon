# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def load_cldr(apps, schema_editor):
    CLDR_Plurals = apps.get_model('base', 'CLDR_Plurals')
    CLDR = ["zero", "one", "two", "few", "many", "other"]

    for name in CLDR:
        CLDR_Plurals.objects.create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20150627_1202'),
    ]

    operations = [
        migrations.RunPython(load_cldr),
    ]
