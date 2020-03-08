# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import migrations
import jsonfield.fields


def migrate_old_source_fields(apps, schema_editor):
    """Convert source fields to valid JSON."""
    Entity = apps.get_model("base", "Entity")
    for entity in Entity.objects.all():
        try:
            entity.source = json.dumps(eval(entity.source))
        except SyntaxError:
            if entity.source:
                entity.source = json.dumps([entity.source])
            else:
                entity.source = "[]"
        entity.save()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0016_auto_20150810_1301"),
    ]

    operations = [
        migrations.RunPython(
            migrate_old_source_fields,
            migrations.RunPython.noop,  # JSON is valid Python
            elidable=True,
        ),
        migrations.AlterField(
            model_name="entity",
            name="source",
            field=jsonfield.fields.JSONField(default=list, blank=True),
        ),
    ]
