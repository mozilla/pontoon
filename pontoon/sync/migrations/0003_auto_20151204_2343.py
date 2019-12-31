# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sync", "0002_auto_20151117_0029"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectsynclog",
            name="skipped",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="projectsynclog",
            name="skipped_end_time",
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="repositorysynclog",
            name="end_time",
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
    ]
