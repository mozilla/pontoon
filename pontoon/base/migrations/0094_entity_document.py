# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-02 09:17
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import TextField, Value
from django.db.models.functions import Concat

from pontoon.db.migrations import (
    MultiFieldTRGMIndex,
)


def set_entity_document(apps, schema_editor):
    Entity = apps.get_model('base', 'Entity')
    Entity.objects.update(
        document=Concat('key', Value(' '), 'string', Value(' '), 'string_plural', Value(' '), 'comment')
    )

entity_document_update_trigger_create_sql = """
    CREATE FUNCTION base_translation_entity_document_update() RETURNS TRIGGER AS $$
        BEGIN
          NEW.entity_document = (
            SELECT (e.key || ' ' || e.string || ' ' || e.string_plural || ' ' || e.comment) as document
            FROM base_entity as e
            WHERE id=NEW.entity_id
          );
        RETURN NEW;
    END;
    $$ LANGUAGE 'plpgsql';
    CREATE TRIGGER base_translation_entity_document_update BEFORE INSERT OR UPDATE ON "base_translation"
    FOR EACH ROW EXECUTE PROCEDURE base_translation_entity_document_update()
"""

entity_document_update_trigger_drop_sql = '''
    DROP TRIGGER base_translation_entity_document_update ON "base_translation";
    DROP FUNCTION base_translation_entity_document_update();
'''


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0093_auto_20170517_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='document',
            field=TextField(blank=True),
        ),

        migrations.RunPython(set_entity_document, migrations.RunPython.noop),

        migrations.RunSQL(
            entity_document_update_trigger_drop_sql,
            entity_document_update_trigger_create_sql,
        ),

        MultiFieldTRGMIndex(
            table='base_entity',
            from_fields=['document'],
            field='document'
        ),

        MultiFieldTRGMIndex(
            table='base_translation',
            from_fields=['string'],
            field='string'
        ),
    ]
