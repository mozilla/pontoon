# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pontoon.base.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20150602_0616'),
    ]

    operations = [
        migrations.AddField(
            model_name='locale',
            name='cldr_plurals',
            field=models.CommaSeparatedIntegerField(blank=True, max_length=11, verbose_name=b'CLDR Plurals', validators=[pontoon.base.models.validate_cldr]),
        ),
        migrations.AlterField(
            model_name='resource',
            name='format',
            field=models.CharField(blank=True, max_length=20, verbose_name=b'Format', choices=[(b'po', b'po'), (b'xliff', b'xliff'), (b'properties', b'properties'), (b'dtd', b'dtd'), (b'inc', b'inc'), (b'ini', b'ini'), (b'lang', b'lang'), (b'l20n', b'l20n')]),
        ),
        migrations.AlterField(
            model_name='translation',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
