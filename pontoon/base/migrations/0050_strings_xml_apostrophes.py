# Generated by Django 3.2.15 on 2023-11-15 00:23

from django.db import migrations
from django.db.models import Value
from django.db.models.functions import Replace


def unescape_strings_xml_apostrophes(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(
        resource__format="xml",
        string__contains="\\'",
    )
    entities.update(string=Replace("string", Value("\\'"), Value("'")))

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(
        entity__resource__format="xml",
        string__contains="\\'",
    )
    translations.update(string=Replace("string", Value("\\'"), Value("'")))

    TranslationMemoryEntry = apps.get_model("base", "TranslationMemoryEntry")
    tm_entries = TranslationMemoryEntry.objects.filter(
        entity__resource__format="xml",
    )
    source_tm_entries = tm_entries.filter(source__contains="\\'")
    source_tm_entries.update(source=Replace("source", Value("\\'"), Value("'")))
    target_tm_entries = tm_entries.filter(target__contains="\\'")
    target_tm_entries.update(target=Replace("target", Value("\\'"), Value("'")))


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0049_fix_pluralform_data"),
    ]

    operations = [
        migrations.RunPython(
            code=unescape_strings_xml_apostrophes,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
