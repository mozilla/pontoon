from math import ceil

from moz.l10n.formats import Format
from moz.l10n.formats.fluent import fluent_parse_entry
from moz.l10n.message import message_to_json, parse_message
from moz.l10n.model import CatchallKey, PatternMessage, SelectMessage

from django.db import migrations, models


batch_size = 3000


def set_value_and_properties(apps, schema_editor):
    Resource = apps.get_model("base", "Resource")
    Translation = apps.get_model("base", "Translation")

    batch_total = ceil(Translation.objects.count() / batch_size)
    batch_count = 0

    def print_progress():
        nonlocal batch_count
        batch_count += 1
        if batch_count % 10 == 0 or batch_count == batch_total:
            print(
                f"Progress: {batch_count}/{batch_total} ({batch_count / batch_total:.1%})",
                flush=True,
            )

    pv_trans = []
    v_trans = []
    format_q = models.Subquery(
        Resource.objects.filter(id=models.OuterRef("entity__resource_id")).values(
            "format"
        )
    )
    for trans in Translation.objects.annotate(format=format_q).iterator():
        string = trans.string
        try:
            match trans.format:
                case "fluent":
                    fe = fluent_parse_entry(string, with_linepos=False)
                    msg = fe.value
                    trans.properties = {
                        name: message_to_json(msg)
                        for name, msg in fe.properties.items()
                    } or None
                case "lang" | "properties" | "":
                    msg = PatternMessage([string])
                case "android" | "gettext" | "webext" | "xcode" | "xliff":
                    msg = parse_message(Format.mf2, string)
                case _:
                    msg = parse_message(Format[trans.format], string)

            # MF2 syntax does not retain the catchall name/label
            if isinstance(msg, SelectMessage) and trans.format != "fluent":
                for keys in msg.variants:
                    for key in keys:
                        if isinstance(key, CatchallKey):
                            key.value = "other"

            trans.value = message_to_json(msg)
            if trans.properties:
                pv_trans.append(trans)
            else:
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
    dependencies = [("base", "0110_add_translation_value_and_properties_schema")]

    operations = [
        migrations.RunPython(
            set_value_and_properties, reverse_code=migrations.RunPython.noop
        ),
    ]
