# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-12 15:51
from __future__ import unicode_literals

from django.db import connection, migrations


def delete_ftl_duplicates(apps, schema):
    """
    In the past we fixed a bug that prevented duplicate FTL translations from
    being stored for the same entity and locale. However, we didn't run a data
    migration to clean up the old duplicates. That's why we're doing it now.

    See bug 1405256 for more details.
    """
    Translation = apps.get_model('base', 'Translation')
    TranslationMemoryEntry = apps.get_model('base', 'TranslationMemoryEntry')

    duplicates = []

    with connection.cursor() as cursor:
        cursor.execute("""
            WITH d AS (
                SELECT
                    entity_id,
                    locale_id,
                    t.string,
                    COUNT(t.id) AS duplicates,
                    ARRAY_AGG(t.id ORDER BY approved DESC, rejected ASC, date DESC) AS ids
                FROM base_translation t
                JOIN base_entity e ON (t.entity_id=e.id)
                JOIN base_resource r ON (e.resource_id=r.id)
                WHERE r.format = 'ftl'
                GROUP BY locale_id, entity_id, t.string
                ORDER BY COUNT(t.id) DESC
            )
            SELECT UNNEST(ids[2:100]) FROM d;
        """)
        # Note: Postgres does not support the [2:] syntax.

        duplicates = [duplicate[0] for duplicate in cursor.fetchall()]

        translations = Translation.objects.filter(pk__in=duplicates)
        tms = TranslationMemoryEntry.objects.filter(translation__pk__in=duplicates)

        # Delete TranslationMemoryEntry instances first, because the tms QuerySet
        # gets empty after the Translation instances are deleted.
        tms.delete()
        translations.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0116_bug_1441020_ftl_0_6_4'),
    ]

    operations = [
        migrations.RunPython(
            delete_ftl_duplicates,
            migrations.RunPython.noop
        )
    ]
