from django.db import migrations


def add_trailing_fluent_newlines(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    Translation = apps.get_model("base", "Translation")

    entities = Entity.objects.filter(resource__format="fluent").exclude(
        string__endswith="\n"
    )
    for entity in entities:
        entity.string += "\n"
    Entity.objects.bulk_update(entities, ["string"])

    translations = Translation.objects.filter(entity__resource__format="fluent").exclude(
        string__endswith="\n"
    )
    for trans in translations:
        trans.string += "\n"
    Translation.objects.bulk_update(translations, ["string"], batch_size=10_000)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0098_fix_gettext_translationmemory"),
    ]

    operations = [
        migrations.RunPython(
            add_trailing_fluent_newlines, reverse_code=migrations.RunPython.noop
        ),
    ]
