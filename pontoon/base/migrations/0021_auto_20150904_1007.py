# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def remove_pa_fy(apps, schema_editor):
    Locale = apps.get_model("base", "Locale")

    for code in ["pa", "fy"]:
        l = Locale.objects.get(code=code)
        l.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0020_auto_20150904_0857"),
    ]

    operations = [migrations.RunPython(remove_pa_fy)]
