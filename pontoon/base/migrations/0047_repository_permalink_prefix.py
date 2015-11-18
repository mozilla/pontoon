# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0046_add_force_suggestions'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='permalink_prefix',
            field=models.CharField(max_length=2000, verbose_name=b'Permalink prefix', blank=True),
        ),
    ]
