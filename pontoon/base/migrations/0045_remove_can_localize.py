# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0044_locale_translators"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="project",
            options={"permissions": (("can_manage", "Can manage projects"),)},
        ),
    ]
