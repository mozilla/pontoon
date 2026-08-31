from django.db import migrations


def set_tutorial_entity_value(apps, schema_editor):
    """
    Backfill the message data model `value` for Tutorial entities that were
    created without it.
    """
    Entity = apps.get_model("base", "Entity")

    entities = Entity.objects.filter(resource__project__slug="tutorial", value=[])
    for entity in entities:
        entity.value = [entity.string]
    Entity.objects.bulk_update(entities, ["value"], batch_size=10_000)


class Migration(migrations.Migration):
    dependencies = [
        ("tour", "0002_make_tutorial_public"),
    ]

    operations = [
        migrations.RunPython(
            set_tutorial_entity_value, reverse_code=migrations.RunPython.noop
        ),
    ]
