# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20150703_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='last_dumped',
            field=models.DateTimeField(null=True),
        ),
    ]
