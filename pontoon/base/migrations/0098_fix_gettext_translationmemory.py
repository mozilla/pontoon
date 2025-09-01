from moz.l10n.formats.mf2 import mf2_parse_message
from moz.l10n.message import serialize_message
from moz.l10n.model import CatchallKey, PatternMessage, SelectMessage

from django.db import migrations, models


def fix_string(string: str) -> str:
    # Matches implementation in pontoon/base/simple_preview.py
    msg = mf2_parse_message(string)
    if isinstance(msg, SelectMessage):
        msg = PatternMessage(
            next(
                pattern
                for keys, pattern in msg.variants.items()
                if all(isinstance(key, CatchallKey) for key in keys)
            )
        )
    return serialize_message(None, msg)


def fix_gettext_translationmemory(apps, schema_editor):
    TranslationMemoryEntry = apps.get_model("base", "TranslationMemoryEntry")

    tm_entries = TranslationMemoryEntry.objects.filter(
        entity__resource__format="gettext"
    ).filter(models.Q(source__contains="\\{") | models.Q(target__contains="\\{"))
    for tm in tm_entries:
        tm.source = fix_string(tm.source)
        tm.target = fix_string(tm.target)
    TranslationMemoryEntry.objects.bulk_update(tm_entries, ["source", "target"])


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0097_add_entity_value_and_properties_data"),
    ]

    operations = [
        migrations.RunPython(
            fix_gettext_translationmemory, reverse_code=migrations.RunPython.noop
        ),
    ]
