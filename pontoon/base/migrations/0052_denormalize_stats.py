# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0051_add_related_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='locale',
            name='approved_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='locale',
            name='fuzzy_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='locale',
            name='total_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='locale',
            name='translated_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='approved_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='fuzzy_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='total_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='translated_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='projectlocale',
            name='approved_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='projectlocale',
            name='fuzzy_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='projectlocale',
            name='total_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='projectlocale',
            name='translated_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
