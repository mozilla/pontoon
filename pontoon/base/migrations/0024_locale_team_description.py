# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_auto_20150916_0642'),
    ]

    operations = [
        migrations.AddField(
            model_name='locale',
            name='team_description',
            field=models.TextField(blank=True),
        ),
    ]
