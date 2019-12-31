# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields
import pontoon.base.models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0009_auto_20150721_1511"),
    ]

    operations = [
        migrations.AddField(
            model_name="translation",
            name="extra",
            field=jsonfield.fields.JSONField(default=pontoon.base.models.extra_default),
        ),
    ]
