from re import Match, compile

from django.db import migrations
from django.db.models import Q


ws_around_outer_tag = compile(r"^\s+(?=<)|(?<=>)\s+$")
ws_before_block_tag = compile(r"\s+(?=<(br|label|li|p|/?ul)\b)")
ws_after_br = compile(r"((?<=<br>)|(?<=<br/>)|(?<=\\n))\s+")
ws_multiple = compile(r"\s\s+|[^\S \n]")
esc_quotes = compile(r"\\(['\"])")
esc_nl = compile(r"\\\n *")
esc_u = compile(r"\\u[0-9A-Fa-f]{4}")


def fix_android_string(string: str):
    string = ws_around_outer_tag.sub("", string)
    string = ws_before_block_tag.sub("\n", string)
    string = ws_after_br.sub("\n", string)
    string = ws_multiple.sub(" ", string)
    string = esc_quotes.sub(r"\1", string)
    return string


def fix_android(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    android_entities = Entity.objects.filter(resource__format="xml")
    for ent in android_entities:
        ent.string = fix_android_string(ent.string)
    Entity.objects.bulk_update(android_entities, ["string"])

    Translation = apps.get_model("base", "Translation")
    android_translations = Translation.objects.filter(entity__resource__format="xml")
    for trans in android_translations:
        trans.string = fix_android_string(trans.string)
    Translation.objects.bulk_update(android_translations, ["string"], batch_size=2000)


def fix_ini(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(resource__format="ini", string__endswith=" ")
    for ent in entities:
        ent.string = ent.string.rstrip()
    Entity.objects.bulk_update(entities, ["string"])

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(
        entity__resource__format="ini", string__endswith=" "
    )
    for trans in translations:
        trans.string = trans.string.rstrip()
    Translation.objects.bulk_update(translations, ["string"], batch_size=2000)


def prop_unescape(m: Match[str]):
    src = m[0]
    if src == "\\u0000":
        return src
    if src == "\\u000A" or src == "\\u000a":
        return "\\n"
    return src.encode("utf-8").decode("unicode_escape")


def fix_props(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    prop_entities = Entity.objects.filter(resource__format="properties").filter(
        Q(string__contains="\\\n") | Q(string__contains="\\u")
    )
    for ent in prop_entities:
        ent.string = esc_nl.sub("", ent.string)
        ent.string = esc_u.sub(prop_unescape, ent.string)
    Entity.objects.bulk_update(prop_entities, ["string"])

    Translation = apps.get_model("base", "Translation")
    prop_translations = Translation.objects.filter(
        entity__resource__format="properties"
    ).filter(Q(string__contains="\\\n") | Q(string__contains="\\u"))
    for trans in prop_translations:
        trans.string = esc_nl.sub("", trans.string)
        trans.string = esc_u.sub(prop_unescape, trans.string)
    Translation.objects.bulk_update(prop_translations, ["string"], batch_size=2000)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0073_alter_permissionchangelog_performed_on"),
    ]

    operations = [
        migrations.RunPython(code=fix_android, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(code=fix_ini, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(code=fix_props, reverse_code=migrations.RunPython.noop),
    ]
