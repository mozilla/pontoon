# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20150515_0927'),
    ]

    operations = [
        migrations.AddField(
            model_name='subpage',
            name='resource',
            field=models.ManyToManyField(to='base.Resource', blank=True),
        ),
        migrations.AlterField(
            model_name='translation',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
