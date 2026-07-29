from moz.l10n.formats.fluent import fluent_parse_entry
from moz.l10n.message import message_to_json

from django.db import migrations


def reparse_multi_pattern_fluent(apps, schema_editor):
    """
    Applies the current moz.l10n Fluent parser, so for rollback,
    the previous moz.l10n version (0.12.0) needs to be available.
    """
    Entity = apps.get_model("base", "Entity")
    Translation = apps.get_model("base", "Translation")

    value_entities = Entity.objects.filter(
        resource__format="fluent", value__has_key="decl"
    )
    for e in value_entities:
        msg = fluent_parse_entry(e.string)
        e.value = message_to_json(msg.value)
    Entity.objects.bulk_update(value_entities, ["value"], batch_size=10_000)

    # The `@?` JSON operator is not directly supported by Django
    prop_entities = Entity.objects.raw("""
        SELECT * FROM base_entity e
        JOIN base_resource r ON r.id = e.resource_id
        WHERE r.format = 'fluent' AND e.properties @? '$.*.decl'
    """)
    for e in prop_entities:
        msg = fluent_parse_entry(e.string)
        e.properties = {k: message_to_json(v) for k, v in msg.properties.items()}
    Entity.objects.bulk_update(prop_entities, ["properties"], batch_size=10_000)

    value_translations = Translation.objects.filter(
        entity__resource__format="fluent", value__has_key="decl"
    )
    for t in value_translations:
        msg = fluent_parse_entry(t.string)
        t.value = message_to_json(msg.value)
    Translation.objects.bulk_update(value_translations, ["value"], batch_size=10_000)

    prop_translations = Translation.objects.raw("""
        SELECT * FROM base_translation t
        JOIN base_entity e ON e.id = t.entity_id
        JOIN base_resource r ON r.id = e.resource_id
        WHERE r.format = 'fluent' AND t.properties @? '$.*.decl'
    """)
    for t in prop_translations:
        msg = fluent_parse_entry(t.string)
        t.properties = {k: message_to_json(v) for k, v in msg.properties.items()}
    Translation.objects.bulk_update(
        prop_translations, ["properties"], batch_size=10_000
    )


class Migration(migrations.Migration):
    dependencies = [("base", "0121_project_set_locales_from_repo_and_more")]

    operations = [
        migrations.RunPython(
            reparse_multi_pattern_fluent, reverse_code=reparse_multi_pattern_fluent
        ),
    ]
