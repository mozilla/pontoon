# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0021_auto_20150904_1007"),
    ]

    operations = [
        migrations.RemoveField(model_name="locale", name="nplurals",),
    ]
