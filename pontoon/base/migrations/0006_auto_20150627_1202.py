# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20150602_0616'),
    ]

    operations = [
        migrations.CreateModel(
            name='CLDR_Plurals',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=5)),
            ],
        ),
        migrations.AlterField(
            model_name='resource',
            name='format',
            field=models.CharField(blank=True, max_length=20, verbose_name=b'Format', choices=[(b'po', b'po'), (b'xliff', b'xliff'), (b'properties', b'properties'), (b'dtd', b'dtd'), (b'inc', b'inc'), (b'ini', b'ini'), (b'lang', b'lang'), (b'l20n', b'l20n')]),
        ),
        migrations.AddField(
            model_name='locale',
            name='cldr_plurals',
            field=models.ManyToManyField(to='base.CLDR_Plurals', blank=True),
        ),
    ]
