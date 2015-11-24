# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0048_translationmemoryentry_source_fts'),
    ]

    operations = [
        migrations.RunSQL('CREATE INDEX source_length_idx ON base_translationmemoryentry(CHAR_LENGTH(source))',
                          'DROP INDEX source_length_idx')
    ]
