from html import escape
from json import loads
from re import compile

from moz.l10n.formats import Format
from moz.l10n.formats.android import android_serialize_message
from moz.l10n.formats.fluent import fluent_parse_entry
from moz.l10n.message import message_to_json, parse_message
from moz.l10n.model import CatchallKey, Message, PatternMessage, SelectMessage

from django.db import migrations, models


android_nl = compile(r"\s*\n\s*")
android_esc = compile(r"(?<!\\)\\([nt])\s*")


def parse_pontoon_message(
    db_format: str, string: str, meta: list[list[str]]
) -> Message:
    """
    Parse an Entity.string or a Translation.string as a moz.l10n Message.

    TODO: This function should be removed once the string message representations are removed.
    """
    xliff_is_xcode = False
    match db_format:
        case "webext":
            ph = next((loads(v) for k, v in meta if k == "placeholders"), None)
            return parse_message(Format.webext, string, webext_placeholders=ph)
        case "lang" | "properties" | "":
            return PatternMessage([string])

        case "android":
            format = Format.android
            string = android_nl.sub(" ", string)
            string = android_esc.sub(lambda m: "\n" if m[1] == "n" else "\t", string)
            string = android_serialize_message(string, allow_cdata=True)
        case "gettext":
            format = Format.mf2
        case "xcode":
            format = Format.xliff
            string = escape(string)
            xliff_is_xcode = True
        case "xliff":
            format = Format.xliff
            string = escape(string)
        case _:
            format = Format[db_format]
    return parse_message(format, string, xliff_is_xcode=xliff_is_xcode)


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
