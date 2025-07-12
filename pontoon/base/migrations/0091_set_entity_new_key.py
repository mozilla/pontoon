from django.db import migrations, models


def set_new_key(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    Resource = apps.get_model("base", "Resource")

    entities = Entity.objects.all().annotate(
        format=models.Subquery(
            Resource.objects.filter(id=models.OuterRef("resource_id")).values("format")
        )
    )
    for entity in entities:
        key = entity.old_key.split("\x04")
        if entity.format == "po":
            # Let's put the context after the source string, unlike before
            key.reverse()
        elif entity.format == "ini":
            key = ["Strings"] + key
        entity.new_key = key
    Entity.objects.bulk_update(entities, ["new_key"], batch_size=10_000)


def set_old_key(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    Resource = apps.get_model("base", "Resource")

    entities = Entity.objects.all().annotate(
        format=models.Subquery(
            Resource.objects.filter(id=models.OuterRef("resource_id")).values("format")
        )
    )
    for entity in entities:
        key = entity.new_key
        if entity.format == "po":
            key.reverse()
        elif entity.format == "ini" and key[0] == "Strings":
            key = key[1:]
        entity.old_key = "\x04".join(key)
    Entity.objects.bulk_update(entities, ["old_key"], batch_size=10_000)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0090_add_entity_new_key"),
    ]

    operations = [
        migrations.RunPython(set_new_key, reverse_code=set_old_key),
    ]
