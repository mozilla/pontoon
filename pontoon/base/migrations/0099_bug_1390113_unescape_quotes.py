# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-14 14:32
from __future__ import unicode_literals

from bulk_update.helper import bulk_update

from django.db import migrations
from django.db.models import Q


def unescape_quotes(apps, schema_editor):
    Translation = apps.get_model('base', 'Translation')
    translations_to_update = []
    translations = Translation.objects.filter(
        entity__resource__path__contains="mobile/android/base"
    )

    for translation in translations.filter(
        Q(string__contains="\u0022") |
        Q(string__contains="\u0027")
    ):
        translation.string = translation.string.replace('\\u0022', '"').replace('\\u0027', "'")
        translations_to_update.append(translation)

    bulk_update(translations_to_update, update_fields=['string'])


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0098_move_ms_locales_to_db'),
    ]

    operations = [
        migrations.RunPython(
            unescape_quotes,
            migrations.RunPython.noop
        ),
    ]
