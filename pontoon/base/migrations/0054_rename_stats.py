# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0053_remove_transifex_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locale',
            old_name='approved_count',
            new_name='approved_strings',
        ),
        migrations.RenameField(
            model_name='locale',
            old_name='fuzzy_count',
            new_name='fuzzy_strings',
        ),
        migrations.RenameField(
            model_name='locale',
            old_name='total_count',
            new_name='total_strings',
        ),
        migrations.RenameField(
            model_name='locale',
            old_name='translated_count',
            new_name='translated_strings',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='approved_count',
            new_name='approved_strings',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='fuzzy_count',
            new_name='fuzzy_strings',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='total_count',
            new_name='total_strings',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='translated_count',
            new_name='translated_strings',
        ),
        migrations.RenameField(
            model_name='projectlocale',
            old_name='approved_count',
            new_name='approved_strings',
        ),
        migrations.RenameField(
            model_name='projectlocale',
            old_name='fuzzy_count',
            new_name='fuzzy_strings',
        ),
        migrations.RenameField(
            model_name='projectlocale',
            old_name='total_count',
            new_name='total_strings',
        ),
        migrations.RenameField(
            model_name='projectlocale',
            old_name='translated_count',
            new_name='translated_strings',
        ),
    ]
