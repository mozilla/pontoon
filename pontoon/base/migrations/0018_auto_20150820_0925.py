# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def change_chinese_plurals(apps, schema_editor):
    Locale = apps.get_model("base", "Locale")
    Translation = apps.get_model("base", "Translation")

    for locale in Locale.objects.filter(name="Chinese"):
        locale.nplurals = 1
        locale.plural_rule = "0"
        locale.cldr_plurals = "5"
        locale.save()

        # Delete plural translations
        Translation.objects.filter(locale=locale, plural_form=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0017_entity_source_jsonfield"),
    ]

    operations = [migrations.RunPython(change_chinese_plurals)]
