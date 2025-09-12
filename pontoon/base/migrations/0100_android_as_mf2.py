from html import unescape
from re import Match, compile

from moz.l10n.formats.android import android_parse_message, android_serialize_message
from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_message

from django.db import migrations

from pontoon.base.simple_preview import android_simple_preview


android_nl = compile(r"\s*\n\s*")
android_esc = compile(r"(?<!\\)\\([nt])\s*")


def db_android_parse(db_source: str):
    clean = android_esc.sub(
        lambda m: "\n" if m[1] == "n" else "\t",
        android_nl.sub(" ", db_source),
    )
    android_source = android_serialize_message(clean)
    return android_parse_message(android_source)


def mf2_string_changed(obj):
    db_source = obj.string
    msg = db_android_parse(db_source)
    mf2_source = mf2_serialize_message(msg)
    if mf2_source == db_source:
        return False
    obj.string = mf2_source
    return True


def mf2_tm_changed(tm):
    changed = False
    src_prev = tm.source
    src_msg = db_android_parse(src_prev)
    src_next = android_simple_preview(src_msg)
    if src_next != src_prev:
        tm.source = src_next
        changed = True
    tgt_prev = tm.target
    tgt_msg = db_android_parse(tgt_prev)
    tgt_next = android_simple_preview(tgt_msg)
    if tgt_next != tgt_prev:
        tm.target = tgt_next
        changed = True
    return changed


def android_as_mf2(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(resource__format="android")
    ent_fixed = [e for e in entities if mf2_string_changed(e)]
    n = Entity.objects.bulk_update(ent_fixed, ["string"], batch_size=10_000)
    print(f" ({n} entities)", end="")

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(entity__resource__format="android")
    trans_fixed = [t for t in translations if mf2_string_changed(t)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} translations)", end="")

    TranslationMemoryEntry = apps.get_model("base", "TranslationMemoryEntry")
    tm_entries = TranslationMemoryEntry.objects.filter(
        entity__resource__format="android"
    )
    tm_fixed = [tm for tm in tm_entries if mf2_tm_changed(tm)]
    n = TranslationMemoryEntry.objects.bulk_update(tm_fixed, ["source", "target"])
    print(f" ({n} TM entries)", end="")


_android_esc_u = compile(r"(?<!\\)\\u[0-9A-Fa-f]{4}")
_android_esc_char = compile(r"(?<!\\)\\([^nt])")
_android_esc_nl = compile(r"(?<!\\)\\n\s*")
_android_ws_around_outer_tag = compile(r"^\s+(?=<)|(?<=>)\s+$")
_android_ws_before_block = compile(r"\s+(?=<(br|label|li|p|/?ul)\b)")
_android_ws_after_block = compile(r"((?<=<br>)|(?<=<br/>)|(?<=</ul>)|(?<=\\n))\s+")


def _unicode_unescape(m: Match[str]):
    return m[0].encode("utf-8").decode("unicode_escape")


def android_db_string(msg):
    string = android_serialize_message(msg)
    string = unescape(string)
    string = _android_esc_u.sub(_unicode_unescape, string)
    string = _android_esc_char.sub(r"\1", string)
    string = _android_esc_nl.sub(r"\\n\n", string)
    string = _android_ws_around_outer_tag.sub("", string)
    string = _android_ws_before_block.sub("\n", string)
    string = _android_ws_after_block.sub("\n", string)
    return string


def android_string_changed(obj):
    mf2_source = obj.string
    msg = mf2_parse_message(mf2_source)
    string = android_db_string(msg)
    if string == mf2_source:
        return False
    obj.string = string
    return True


def android_tm_changed(tm):
    changed = False
    src_prev = tm.entity.string
    src_msg = mf2_parse_message(src_prev)
    src_next = android_db_string(src_msg)
    if src_next != tm.source:
        tm.source = src_next
        changed = True
    tgt_prev = tm.translation.string
    tgt_msg = mf2_parse_message(tgt_prev)
    tgt_next = android_db_string(tgt_msg)
    if tgt_next != tm.target:
        tm.target = tgt_next
        changed = True
    return changed


def mf2_as_android(apps, schema_editor):
    TranslationMemoryEntry = apps.get_model("base", "TranslationMemoryEntry")
    tm_entries = TranslationMemoryEntry.objects.filter(
        entity__resource__format="android",
        translation__isnull=False,
    ).select_related("entity", "translation")
    tm_fixed = [tm for tm in tm_entries if android_tm_changed(tm)]
    n = TranslationMemoryEntry.objects.bulk_update(tm_fixed, ["source", "target"])
    print(f" ({n} TM entries)", end="")

    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(resource__format="android")
    ent_fixed = [e for e in entities if android_string_changed(e)]
    n = Entity.objects.bulk_update(ent_fixed, ["string"], batch_size=10_000)
    print(f" ({n} entities)", end="")

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(entity__resource__format="android")
    trans_fixed = [t for t in translations if android_string_changed(t)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} translations)", end="")


class Migration(migrations.Migration):
    dependencies = [("base", "0099_add_trailing_fluent_newlines")]
    operations = [migrations.RunPython(android_as_mf2, reverse_code=mf2_as_android)]
