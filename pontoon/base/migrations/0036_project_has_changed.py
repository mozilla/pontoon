# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0035_remove_deleted_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='has_changed',
            field=models.BooleanField(default=False),
        ),
    ]
