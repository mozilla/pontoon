# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0008_auto_20150710_0946"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="last_synced",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="translation",
            name="deleted",
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
