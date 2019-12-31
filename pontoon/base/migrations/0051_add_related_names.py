# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0050_auto_20160216_0026"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectlocale",
            name="locale",
            field=models.ForeignKey(related_name="project_locale", to="base.Locale"),
        ),
        migrations.AlterField(
            model_name="projectlocale",
            name="project",
            field=models.ForeignKey(related_name="project_locale", to="base.Project"),
        ),
        migrations.AlterField(
            model_name="stats",
            name="locale",
            field=models.ForeignKey(related_name="stats", to="base.Locale"),
        ),
        migrations.AlterField(
            model_name="stats",
            name="resource",
            field=models.ForeignKey(related_name="stats", to="base.Resource"),
        ),
    ]
