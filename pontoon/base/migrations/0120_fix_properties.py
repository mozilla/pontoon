import json
import re

from moz.l10n.formats.properties import (
    properties_parse_message,
    properties_serialize_message,
)
from moz.l10n.message import message_from_json, message_to_json
from moz.l10n.model import PatternMessage

from django.db import migrations
from django.db.models import Q


_esc_nul = re.compile(r"\\u(?:0|00|000)(?![0-9a-fA-F])|\\u0000")


def _clean_and_parse(src: str):
    clean = src.strip("\n").replace("\n", "\\n")
    clean = _esc_nul.sub(r"\\uFFFD", clean)
    return properties_parse_message(clean)


def fix_properties(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(resource__format="properties").filter(
        Q(string__contains="\\") | Q(string__contains="\n")
    )
    for e in entities:
        msg = properties_parse_message(e.string)
        e.value = message_to_json(msg)
        e.string = properties_serialize_message(msg)
    Entity.objects.bulk_update(entities, ["string", "value"])

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(
        entity__resource__format="properties"
    ).filter(Q(string__contains="\\") | Q(string__contains="\n"))
    for t in translations:
        try:
            msg = _clean_and_parse(t.string)
            t.value = message_to_json(msg)
            t.string = properties_serialize_message(msg)
        except ValueError:
            print(t.entity_id, t.locale.code, json.dumps(t.string))
            raise
    Translation.objects.bulk_update(
        translations, ["string", "value"], batch_size=10_000
    )

    TranslationMemoryEntry = apps.get_model("base", "TranslationMemoryEntry")
    tm_entries = TranslationMemoryEntry.objects.filter(
        entity__resource__format="properties"
    ).filter(Q(source__contains="\\") | Q(target__contains="\\"))
    for tm in tm_entries:
        src_msg = properties_parse_message(tm.source)
        (tm.source,) = src_msg.pattern if src_msg.pattern else [""]
        tgt_msg = _clean_and_parse(tm.target)
        (tm.target,) = tgt_msg.pattern if tgt_msg.pattern else [""]
    TranslationMemoryEntry.objects.bulk_update(tm_entries, ["source", "target"])


_prop_esc_u = re.compile(r"(?<!\\)\\u(?!0000)[0-9A-Fa-f]{4}")
_prop_esc_ws = re.compile(r"(?<!\\)\\([^\S\n])")


def _unicode_unescape(m: re.Match[str]):
    return m[0].encode("utf-8").decode("unicode_escape")


def _unfix_string(msg):
    string = properties_serialize_message(msg)
    string = _prop_esc_u.sub(_unicode_unescape, string)
    string = _prop_esc_ws.sub(r"\1", string)
    return string


def unfix_properties(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(
        resource__format="properties", string__contains="\\"
    )
    for e in entities:
        e.string = _unfix_string(message_from_json(e.value))
        e.value = [e.string]
    Entity.objects.bulk_update(entities, ["string", "value"])

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(
        entity__resource__format="properties", string__contains="\\"
    )
    for t in translations:
        t.string = _unfix_string(message_from_json(t.value))
        t.value = [t.string]
    Translation.objects.bulk_update(
        translations, ["string", "value"], batch_size=10_000
    )

    TranslationMemoryEntry = apps.get_model("base", "TranslationMemoryEntry")
    tm_entries = TranslationMemoryEntry.objects.filter(
        entity__resource__format="properties"
    ).filter(Q(source__contains="\n") | Q(target__contains="\n"))
    for tm in tm_entries:
        tm.source = _unfix_string(PatternMessage([tm.source])) if tm.source else ""
        tm.target = _unfix_string(PatternMessage([tm.target])) if tm.target else ""
    TranslationMemoryEntry.objects.bulk_update(tm_entries, ["source", "target"])


class Migration(migrations.Migration):
    dependencies = [("base", "0119_userprofile_community_health_locales")]

    operations = [
        migrations.RunPython(fix_properties, reverse_code=unfix_properties),
    ]
