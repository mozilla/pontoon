from django.db import migrations


def set_terminology_entity_value(apps, schema_editor):
    """
    Backfill the message data model `value` for Terminology entities that were
    created without it.
    """
    Entity = apps.get_model("base", "Entity")

    entities = Entity.objects.filter(resource__project__slug="terminology", value=[])
    for entity in entities:
        entity.value = [entity.string]
    Entity.objects.bulk_update(entities, ["value"], batch_size=10_000)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0117_userprofile_editor_theme"),
    ]

    operations = [
        migrations.RunPython(
            set_terminology_entity_value, reverse_code=migrations.RunPython.noop
        ),
    ]
