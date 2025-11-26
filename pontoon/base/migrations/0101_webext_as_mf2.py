from json import dumps
from re import compile

from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_message
from moz.l10n.formats.webext import webext_serialize_message
from moz.l10n.message import message_from_json
from moz.l10n.model import Expression, PatternMessage, VariableRef

from django.db import migrations


webext_placeholder = compile(r"\$([a-zA-Z0-9_@]+)\$|(\$[1-9])|\$(\$+)")


def webext_translation_parse(translation):
    db_source = translation.string
    declarations = message_from_json(translation.entity.value).declarations
    pattern = []
    pos = 0
    for m in webext_placeholder.finditer(db_source):
        start = m.start()
        if start > pos:
            pattern.append(db_source[pos:start])
        if m[1]:
            # Named placeholder, with content & optional example in placeholders object
            ph_name = m[1].replace("@", "_")
            if ph_name[0].isdigit():
                ph_name = f"_{ph_name}"
            ph_name = next(
                (name for name in declarations if name.lower() == ph_name.lower()),
                ph_name,
            )
            var = VariableRef(ph_name)
            pattern.append(Expression(var, attributes={"source": m[0]}))
        elif m[2]:
            # Indexed placeholder
            var = VariableRef(f"arg{m[2][1]}")
            pattern.append(Expression(var, attributes={"source": m[0]}))
        else:
            # Escaped literal dollar sign
            if pattern and isinstance(pattern[-1], str):
                pattern[-1] += m[3]
            else:
                pattern.append(m[3])
        pos = m.end()
    if pos < len(db_source):
        pattern.append(db_source[pos:])
    return PatternMessage(pattern, declarations)


def mf2_entity_changed(entity):
    db_source = entity.string
    msg = message_from_json(entity.value)
    mf2_source = mf2_serialize_message(msg)
    if mf2_source == db_source:
        return False
    entity.string = mf2_source
    entity.meta = [m for m in entity.meta if m[0] != "placeholders"]
    return True


def mf2_translation_changed(translation):
    db_source = translation.string
    msg = webext_translation_parse(translation)
    mf2_source = mf2_serialize_message(msg)
    if mf2_source == db_source:
        return False
    translation.string = mf2_source
    return True


def webext_as_mf2(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(resource__format="webext")
    ent_fixed = [e for e in entities if mf2_entity_changed(e)]
    n = Entity.objects.bulk_update(ent_fixed, ["meta", "string"], batch_size=10_000)
    print(f" ({n} entities)", end="", flush=True)

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(
        entity__resource__format="webext"
    ).select_related("entity")
    trans_fixed = [t for t in translations if mf2_translation_changed(t)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} translations)", end="", flush=True)


def webext_string_changed(obj, with_placeholders: bool):
    mf2_source = obj.string
    msg = mf2_parse_message(mf2_source)
    string, placeholders = webext_serialize_message(msg)
    if string == mf2_source:
        return False
    obj.string = string
    if with_placeholders:
        obj.meta.append(["placeholders", dumps(placeholders)])
    return True


def mf2_as_webext(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(resource__format="webext")
    ent_fixed = [e for e in entities if webext_string_changed(e, True)]
    n = Entity.objects.bulk_update(ent_fixed, ["meta", "string"], batch_size=10_000)
    print(f" ({n} entities)", end="", flush=True)

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(entity__resource__format="webext")
    trans_fixed = [t for t in translations if webext_string_changed(t, False)]
    n = Translation.objects.bulk_update(trans_fixed, ["string"], batch_size=10_000)
    print(f" ({n} translations)", end="", flush=True)


class Migration(migrations.Migration):
    dependencies = [("base", "0100_android_as_mf2")]
    operations = [migrations.RunPython(webext_as_mf2, reverse_code=mf2_as_webext)]
