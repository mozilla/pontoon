# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0052_denormalize_stats"),
    ]

    operations = [
        migrations.RemoveField(model_name="project", name="transifex_project",),
        migrations.RemoveField(model_name="project", name="transifex_resource",),
    ]
