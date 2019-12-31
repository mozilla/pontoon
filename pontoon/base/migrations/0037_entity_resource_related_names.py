# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0036_project_has_changed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entity",
            name="resource",
            field=models.ForeignKey(related_name="entities", to="base.Resource"),
        ),
        migrations.AlterField(
            model_name="resource",
            name="project",
            field=models.ForeignKey(related_name="resources", to="base.Project"),
        ),
    ]
