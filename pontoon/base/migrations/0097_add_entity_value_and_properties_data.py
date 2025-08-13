from moz.l10n.formats.fluent import fluent_parse_entry
from moz.l10n.message import message_to_json
from moz.l10n.model import CatchallKey, SelectMessage

from django.db import migrations, models

from pontoon.sync.utils import parse_pontoon_message


def set_value_and_properties(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    Resource = apps.get_model("base", "Resource")

    fluent_entities = Entity.objects.filter(resource__format="fluent")
    for entity in fluent_entities:
        try:
            fe = fluent_parse_entry(entity.string, with_linepos=False)
            entity.value = message_to_json(fe.value)
            entity.properties = {
                name: message_to_json(msg) for name, msg in fe.properties.items()
            } or None
        except Exception:
            if entity.obsolete and entity.resource.project.disabled:
                entity.value = [entity.string]
            else:
                raise
    Entity.objects.bulk_update(
        fluent_entities, ["value", "properties"], batch_size=10_000
    )

    other_entities = Entity.objects.exclude(resource__format="fluent").annotate(
        format=models.Subquery(
            Resource.objects.filter(id=models.OuterRef("resource_id")).values("format")
        )
    )
    for entity in other_entities:
        try:
            msg = parse_pontoon_message(entity.format, entity.string, entity.meta)
            if entity.format == "gettext" and isinstance(msg, SelectMessage):
                for keys in msg.variants:
                    if isinstance(keys[0], CatchallKey):
                        # MF2 syntax does not retain the catchall name/label
                        keys[0].value = "other"
            entity.value = message_to_json(msg)
        except Exception:
            if entity.obsolete and entity.resource.project.disabled:
                entity.value = [entity.string]
            else:
                raise
    Entity.objects.bulk_update(other_entities, ["value"], batch_size=10_000)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0096_add_entity_value_and_properties_schema"),
    ]

    operations = [
        migrations.RunPython(
            set_value_and_properties, reverse_code=migrations.RunPython.noop
        ),
    ]
