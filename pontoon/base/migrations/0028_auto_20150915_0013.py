# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0027_auto_20150910_1735"),
    ]

    operations = [
        migrations.AlterField(
            model_name="repository",
            name="project",
            field=models.ForeignKey(related_name="repositories", to="base.Project"),
        ),
    ]
