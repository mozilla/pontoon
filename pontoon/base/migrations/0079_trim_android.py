from django.db import migrations
from django.db.models import Q


def trim_android(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    android_entities = Entity.objects.filter(resource__format="xml").filter(
        Q(string__startswith=" ") | Q(string__endswith=" ")
    )
    for ent in android_entities:
        ent.string = ent.string.strip()
    Entity.objects.bulk_update(android_entities, ["string"])

    Translation = apps.get_model("base", "Translation")
    android_translations = Translation.objects.filter(
        entity__resource__format="xml"
    ).filter(Q(string__startswith=" ") | Q(string__endswith=" "))
    for trans in android_translations:
        trans.string = trans.string.strip()
    Translation.objects.bulk_update(android_translations, ["string"], batch_size=2000)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0078_alter_userprofile_theme"),
    ]

    operations = [
        migrations.RunPython(code=trim_android, reverse_code=migrations.RunPython.noop),
    ]
