# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_repository_last_synced_revisions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repository',
            name='multi_locale',
        ),
    ]
