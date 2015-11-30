# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0047_repository_permalink_prefix'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntityLocaleStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_suggestions', models.BooleanField(default=False)),
                ('is_translated', models.BooleanField(default=False)),
                ('is_fuzzy', models.BooleanField(default=False)),
                ('is_changed', models.BooleanField(default=False)),
                ('is_approved', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='entity',
            name='string',
            field=models.TextField(db_index=True),
        ),
        migrations.AlterField(
            model_name='entity',
            name='string_plural',
            field=models.TextField(db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='entitylocalestatus',
            name='entity',
            field=models.ForeignKey(related_name='locale_status', to='base.Entity'),
        ),
        migrations.AddField(
            model_name='entitylocalestatus',
            name='locale',
            field=models.ForeignKey(to='base.Locale'),
        ),
        migrations.AlterUniqueTogether(
            name='entitylocalestatus',
            unique_together=set([('entity', 'locale')]),
        ),
    ]
