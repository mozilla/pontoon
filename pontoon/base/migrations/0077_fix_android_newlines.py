from re import compile

from django.db import migrations


def fix_android_newlines(apps, schema_editor):
    esc_nl = compile(r"(?<!\\)\\n\s*")

    Entity = apps.get_model("base", "Entity")
    android_entities = Entity.objects.filter(
        resource__format="xml", string__contains="\\n"
    )
    for ent in android_entities:
        ent.string = esc_nl.sub(r"\\n\n", ent.string)
    Entity.objects.bulk_update(android_entities, ["string"])

    Translation = apps.get_model("base", "Translation")
    android_translations = Translation.objects.filter(
        entity__resource__format="xml", string__contains="\\n"
    )
    for trans in android_translations:
        trans.string = esc_nl.sub(r"\\n\n", trans.string)
    Translation.objects.bulk_update(android_translations, ["string"], batch_size=2000)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0076_remove_pontoon_intro_project"),
    ]

    operations = [
        migrations.RunPython(
            code=fix_android_newlines, reverse_code=migrations.RunPython.noop
        ),
    ]
