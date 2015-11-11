# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sync', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repositorysynclog',
            name='end_time',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True),
        ),
    ]
