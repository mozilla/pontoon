from django.db import migrations
from django.utils import timezone


def delete_more_empty_gettext_plurals(apps, schema_editor):
    ActionLog = apps.get_model("actionlog", "ActionLog")
    User = apps.get_model("auth", "User")
    Translation = apps.get_model("base", "Translation")
    TranslationMemoryEntry = apps.get_model("base", "TranslationMemoryEntry")

    now = timezone.now()
    sync_user = User.objects.get(username="pontoon-sync")

    regex = r"^\.input {\$n :number}\s\.match \$n(\s[a-z*]+ {{}})+$"

    translations = Translation.objects.filter(string__regex=regex)
    ActionLog.objects.bulk_create(
        [
            ActionLog(
                action_type="translation:deleted",
                created_at=now,
                performed_by=sync_user,
                entity_id=t.entity_id,
                locale_id=t.locale_id,
            )
            for t in translations
        ]
    )
    translations.delete()

    tm_entries = TranslationMemoryEntry.objects.filter(target__regex=regex)
    ActionLog.objects.bulk_create(
        [
            ActionLog(
                action_type="tm_entry:deleted",
                created_at=now,
                performed_by=sync_user,
                entity_id=t.entity_id,
                locale_id=t.locale_id,
            )
            for t in tm_entries
        ]
    )
    tm_entries.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0092_del_entity_old_key"),
    ]
    operations = [
        migrations.RunPython(
            delete_more_empty_gettext_plurals, reverse_code=migrations.RunPython.noop
        ),
    ]
