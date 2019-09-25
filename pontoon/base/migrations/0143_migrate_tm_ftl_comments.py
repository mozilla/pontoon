# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-25 18:26
from __future__ import unicode_literals

from bulk_update.helper import bulk_update
from django.db import migrations
from pontoon.base.templatetags.helpers import as_simple_translation


def regenerate_ftl_entries_with_comments(apps, schema):
    """
    Regenerate source column in TranslationMemoryEntry for all FTL strings
    that are potentially comments instead of strings.

    See bug 1581594 for more details.
    """
    TranslationMemoryEntry = apps.get_model('base', 'TranslationMemoryEntry')

    tm_entries = (
        TranslationMemoryEntry.objects
        .filter(entity__resource__format='ftl', source__contains="#")
        .prefetch_related('entity', 'translation')
    )

    for tme in tm_entries:
        tme.source = as_simple_translation(tme.entity.string)

    bulk_update(
        tm_entries,
        update_fields=['source', 'target'],
        batch_size=1000,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0142_migrate_tm_ftl'),
    ]

    operations = [
        migrations.RunPython(
            regenerate_ftl_entries_with_comments,
            migrations.RunPython.noop
        )
    ]
