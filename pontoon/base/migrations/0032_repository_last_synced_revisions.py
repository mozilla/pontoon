# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0031_changedentitylocale_when"),
    ]

    operations = [
        migrations.AddField(
            model_name="repository",
            name="last_synced_revisions",
            field=jsonfield.fields.JSONField(default=dict, blank=True),
        ),
    ]
