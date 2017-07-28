# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-11-23 23:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0070_auto_20161110_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='langpack_url',
            field=models.URLField(
                blank=True, help_text=b'\n        URL pattern for downloading language packs. Leave empty if language packs\n        not available for the project. Supports {locale_code} wildcard.\n    ', null=True, verbose_name=b'Language pack URL'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='format',
            field=models.CharField(blank=True, choices=[(b'po', b'po'), (b'xliff', b'xliff'), (b'xlf', b'xliff'), (b'properties', b'properties'), (
                b'dtd', b'dtd'), (b'inc', b'inc'), (b'ini', b'ini'), (b'lang', b'lang'), (b'ftl', b'ftl')], max_length=20, verbose_name=b'Format'),
        ),
    ]
