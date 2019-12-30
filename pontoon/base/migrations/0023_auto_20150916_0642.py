# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0022_remove_locale_nplurals"),
    ]

    operations = [
        migrations.AlterField(
            model_name="translation",
            name="date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
