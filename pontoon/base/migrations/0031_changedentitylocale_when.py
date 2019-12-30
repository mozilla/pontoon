# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0030_repository_source_repo"),
    ]

    operations = [
        migrations.AddField(
            model_name="changedentitylocale",
            name="when",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
