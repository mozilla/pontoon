# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0046_add_force_suggestions'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationMemoryEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.TextField()),
                ('target', models.TextField()),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='base.Entity', null=True)),
                ('locale', models.ForeignKey(to='base.Locale')),
                ('translation', models.ForeignKey(related_name='memory_entries', on_delete=django.db.models.deletion.SET_NULL, to='base.Translation', null=True)),
            ],
        ),
    ]
