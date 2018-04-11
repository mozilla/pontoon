# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-11 13:36
from __future__ import unicode_literals

from django.db import migrations

from pontoon.base.models import TranslatedResource


def calculate_all_stats(apps, schema_editor):
    translated_resources = TranslatedResource.objects.all()
    for tr in translated_resources:
        tr.calculate_stats()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0119_rename_translated_to_unreviewed'),
    ]

    operations = [
        migrations.RunPython(
            calculate_all_stats,
            migrations.RunPython.noop
        ),
    ]
