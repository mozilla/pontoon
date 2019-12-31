# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0039_projectlocales_unique"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="locale",
            options={
                "ordering": ["name", "code"],
                "permissions": (
                    ("can_translate_locale", "Can add translations"),
                    ("can_manage_locale", "Can manage locale"),
                ),
            },
        ),
    ]
