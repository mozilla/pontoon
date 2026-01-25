from html import escape
from re import compile

from moz.l10n.formats.android import android_parse_message, android_serialize_message
from moz.l10n.formats.mf2 import mf2_serialize_message
from moz.l10n.formats.xliff import xliff_parse_message

from django.db import migrations


android_nl = compile(r"\s*\n\s*")
android_esc = compile(r"(?<!\\)\\([nt])\s*")


def android_translation_changed(obj):
    db_source = obj.string
    clean = android_esc.sub(
        lambda m: "\n" if m[1] == "n" else "\t",
        android_nl.sub(" ", db_source),
    )
    android_source = android_serialize_message(clean)
    msg = android_parse_message(android_source)
    mf2_source = mf2_serialize_message(msg)
    if mf2_source == db_source:
        return False
    obj.string = mf2_source
    return True


def android_as_mf2(apps, schema_editor):
    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(
        entity__resource__format="android", string__contains="$"
    ).exclude(string__contains="{")
    trans_fixed = [t for t in translations if android_translation_changed(t)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} android translations)", end="")


def xliff_translation_changed(translation, is_xcode: bool):
    db_source = translation.string
    msg = xliff_parse_message(escape(db_source), is_xcode=is_xcode)
    mf2_source = mf2_serialize_message(msg)
    if mf2_source == db_source:
        return False
    translation.string = mf2_source
    return True


def xliff_as_mf2(apps, schema_editor):
    Translation = apps.get_model("base", "Translation")

    translations = (
        Translation.objects.filter(
            entity__resource__format="xcode", string__contains="$"
        )
        .exclude(string__contains="{")
        .select_related("entity")
    )
    trans_fixed = [t for t in translations if xliff_translation_changed(t, True)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} xcode translations)", end="", flush=True)

    translations = (
        Translation.objects.filter(
            entity__resource__format="xliff", string__contains="$"
        )
        .exclude(string__contains="{")
        .select_related("entity")
    )
    trans_fixed = [t for t in translations if xliff_translation_changed(t, False)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} xliff translations)", end="", flush=True)


class Migration(migrations.Migration):
    dependencies = [("base", "0104_remove_project_langpack_url")]
    operations = [
        migrations.RunPython(android_as_mf2, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(xliff_as_mf2, reverse_code=migrations.RunPython.noop),
    ]
