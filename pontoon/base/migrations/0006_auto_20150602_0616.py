# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20150703_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='format',
            field=models.CharField(blank=True, max_length=20, verbose_name=b'Format', choices=[(b'po', b'po'), (b'xliff', b'xliff'), (b'properties', b'properties'), (b'dtd', b'dtd'), (b'inc', b'inc'), (b'ini', b'ini'), (b'lang', b'lang')]),
        ),
    ]
