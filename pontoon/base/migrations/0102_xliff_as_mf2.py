from html import escape, unescape

from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_message
from moz.l10n.formats.xliff import xliff_parse_message, xliff_serialize_message
from moz.l10n.message import message_from_json

from django.db import migrations


def mf2_entity_changed(entity):
    db_source = entity.string
    msg = message_from_json(entity.value)
    mf2_source = mf2_serialize_message(msg)
    if mf2_source == db_source:
        return False
    entity.string = mf2_source
    return True


def mf2_translation_changed(translation, is_xcode: bool):
    db_source = translation.string
    msg = xliff_parse_message(escape(db_source), is_xcode=is_xcode)
    mf2_source = mf2_serialize_message(msg)
    if mf2_source == db_source:
        return False
    translation.string = mf2_source
    return True


def xliff_as_mf2(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    Translation = apps.get_model("base", "Translation")

    entities = Entity.objects.filter(resource__format__in=["xliff", "xcode"])
    ent_fixed = [e for e in entities if mf2_entity_changed(e)]
    n = Entity.objects.bulk_update(ent_fixed, ["string"], batch_size=10_000)
    print(f" ({n} entities)", end="", flush=True)

    translations = Translation.objects.filter(
        entity__resource__format="xcode"
    ).select_related("entity")
    trans_fixed = [t for t in translations if mf2_translation_changed(t, True)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} xcode translations)", end="", flush=True)

    translations = Translation.objects.filter(
        entity__resource__format="xliff"
    ).select_related("entity")
    trans_fixed = [t for t in translations if mf2_translation_changed(t, False)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} xliff translations)", end="", flush=True)


def xliff_string_changed(obj):
    mf2_source = obj.string
    msg = mf2_parse_message(mf2_source)
    string = unescape(xliff_serialize_message(msg))
    if string == mf2_source:
        return False
    obj.string = string
    return True


def mf2_as_xliff(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(resource__format__in=["xliff", "xcode"])
    ent_fixed = [e for e in entities if xliff_string_changed(e)]
    n = Entity.objects.bulk_update(ent_fixed, ["meta", "string"], batch_size=10_000)
    print(f" ({n} entities)", end="", flush=True)

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(
        entity__resource__format__in=["xliff", "xcode"]
    )
    trans_fixed = [t for t in translations if xliff_string_changed(t)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} translations)", end="", flush=True)


class Migration(migrations.Migration):
    dependencies = [("base", "0101_webext_as_mf2")]
    operations = [migrations.RunPython(xliff_as_mf2, reverse_code=mf2_as_xliff)]
