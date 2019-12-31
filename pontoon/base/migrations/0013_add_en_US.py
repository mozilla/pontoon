# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_back_source_locales(apps, schema_editor):
    Locale = apps.get_model("base", "Locale")
    Locale.objects.create(
        code="en",
        name="English",
        nplurals=2,
        plural_rule="(n != 1)",
        cldr_plurals="1,5",
    )
    Locale.objects.create(
        code="en-US",
        name="English",
        nplurals=2,
        plural_rule="(n != 1)",
        cldr_plurals="1,5",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0012_auto_20150804_0859"),
    ]

    operations = [migrations.RunPython(add_back_source_locales)]
