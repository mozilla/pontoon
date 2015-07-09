# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_project_last_dumped'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='last_dumped',
            new_name='last_committed',
        ),
    ]
