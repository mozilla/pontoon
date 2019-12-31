# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0003_auto_user_profile_related_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resource",
            name="format",
            field=models.CharField(
                blank=True,
                max_length=20,
                verbose_name=b"Format",
                choices=[
                    (b"po", b"po"),
                    (b"xliff", b"xliff"),
                    (b"properties", b"properties"),
                    (b"dtd", b"dtd"),
                    (b"ini", b"ini"),
                    (b"lang", b"lang"),
                ],
            ),
        ),
    ]
