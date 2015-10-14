# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_auto_20150820_0925'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='locale',
            options={'ordering': ['name', 'code']},
        ),
        migrations.RenameField(
            model_name='subpage',
            old_name='resource',
            new_name='resources',
        ),
    ]
