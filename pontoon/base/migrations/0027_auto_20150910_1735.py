# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0026_migrate_repository_info"),
    ]

    operations = [
        migrations.RemoveField(model_name="project", name="repository_path",),
        migrations.RemoveField(model_name="project", name="repository_type",),
        migrations.RemoveField(model_name="project", name="repository_url",),
    ]
