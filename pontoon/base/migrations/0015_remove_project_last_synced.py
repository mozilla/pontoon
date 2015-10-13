# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20150806_0948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='last_synced',
        ),
    ]
