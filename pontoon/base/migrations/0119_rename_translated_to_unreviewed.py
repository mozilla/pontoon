# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-21 15:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0118_project_contribs_index'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locale',
            old_name='translated_strings',
            new_name='unreviewed_strings',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='translated_strings',
            new_name='unreviewed_strings',
        ),
        migrations.RenameField(
            model_name='projectlocale',
            old_name='translated_strings',
            new_name='unreviewed_strings',
        ),
        migrations.RenameField(
            model_name='translatedresource',
            old_name='translated_strings',
            new_name='unreviewed_strings',
        ),
    ]
