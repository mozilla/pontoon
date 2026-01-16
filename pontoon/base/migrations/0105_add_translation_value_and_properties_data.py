from math import ceil

from moz.l10n.formats import Format
from moz.l10n.formats.fluent import fluent_parse_entry
from moz.l10n.message import message_to_json, parse_message
from moz.l10n.model import CatchallKey, Message, PatternMessage, SelectMessage

from django.db import migrations, models


batch_size = 10000


def parse_pontoon_message(trans) -> Message:
    string = trans.string
    match trans.format:
        case "lang" | "properties" | "":
            return PatternMessage([string])
        case "android" | "gettext" | "webext" | "xcode" | "xliff":
            format = Format.mf2
        case _:
            format = Format[trans.format]
    msg = parse_message(format, string)
    if isinstance(msg, SelectMessage):
        for keys in msg.variants:
            for key in keys:
                if isinstance(key, CatchallKey):
                    # MF2 syntax does not retain the catchall name/label
                    key.value = "other"
    return msg


def set_value_and_properties(apps, schema_editor):
    Resource = apps.get_model("base", "Resource")
    Translation = apps.get_model("base", "Translation")

    batch_total = ceil(Translation.objects.count() / batch_size)
    batch_count = 0

    def print_progress():
        nonlocal batch_count
        if batch_count % 10 == 0:
            print(f".({(batch_count / batch_total):.1%})", end="", flush=True)
        else:
            print(".", end="", flush=True)
        batch_count += 1

    pv_trans = []
    v_trans = []
    format_q = models.Subquery(
        Resource.objects.filter(id=models.OuterRef("entity__resource_id")).values(
            "format"
        )
    )
    for trans in Translation.objects.annotate(format=format_q).iterator():
        try:
            if trans.format == "fluent":
                fe = fluent_parse_entry(trans.string, with_linepos=False)
                trans.value = message_to_json(fe.value)
                trans.properties = {
                    name: message_to_json(msg) for name, msg in fe.properties.items()
                } or None
                if trans.properties:
                    pv_trans.append(trans)
                else:
                    v_trans.append(trans)
            else:
                msg = parse_pontoon_message(trans)
                trans.value = message_to_json(msg)
                v_trans.append(trans)
        except Exception:
            if (
                trans.approved
                and not trans.entity.obsolete
                and not trans.entity.resource.project.disabled
            ):
                print(
                    f"\nUsing fallback value for approved and active {trans.format} translation {trans.pk} "
                    f"for entity {trans.entity.pk}, locale {trans.locale.code}:\n{trans.string}",
                    flush=True,
                )
            trans.value = [trans.string]
            v_trans.append(trans)
        if len(pv_trans) == batch_size:
            Translation.objects.bulk_update(pv_trans, ["value", "properties"])
            pv_trans.clear()
            print_progress()
        if len(v_trans) == batch_size:
            Translation.objects.bulk_update(v_trans, ["value"])
            v_trans.clear()
            print_progress()
    if pv_trans:
        Translation.objects.bulk_update(pv_trans, ["value", "properties"])
        print_progress()
    if v_trans:
        Translation.objects.bulk_update(v_trans, ["value"])
        print_progress()


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0104_add_translation_value_and_properties_schema"),
    ]

    operations = [
        migrations.RunPython(
            set_value_and_properties, reverse_code=migrations.RunPython.noop
        ),
    ]
