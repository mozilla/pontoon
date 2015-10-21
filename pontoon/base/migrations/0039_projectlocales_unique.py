# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0038_add_latest_translation'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='projectlocale',
            unique_together=set([('project', 'locale')]),
        ),
    ]
