# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.postgres.operations import CreateExtension
import pg_fts.fields
from pg_fts.migrations import CreateFTSIndexOperation, CreateFTSTriggerOperation


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0047_translationmemoryentry'),
    ]

    operations = [
        CreateExtension("pg_trgm"),
        migrations.AddField(
            model_name='translationmemoryentry',
            name='source_fts',
            field=pg_fts.fields.TSVectorField(dictionary=b'simple', default='', fields=(b'source',), serialize=False, editable=False, null=True),
        ),
        CreateFTSTriggerOperation(
            'TranslationMemoryEntry',
            'source_fts'
        ),
        CreateFTSIndexOperation(
            'TranslationMemoryEntry',
            'source_fts',
            'gin'
        ),
    ]
