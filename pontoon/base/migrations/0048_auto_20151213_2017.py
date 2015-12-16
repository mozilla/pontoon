# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0047_repository_permalink_prefix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='string',
            field=models.TextField(db_index=True),
        ),
        migrations.AlterField(
            model_name='entity',
            name='string_plural',
            field=models.TextField(db_index=True, blank=True),
        ),
    ]
