from django.db import migrations
from django.utils import timezone


def delete_empty_gettext_plurals(apps, schema_editor):
    ActionLog = apps.get_model("actionlog", "ActionLog")
    User = apps.get_model("auth", "User")
    Translation = apps.get_model("base", "Translation")

    now = timezone.now()
    sync_user = User.objects.get(username="pontoon-sync")

    mf2_empty_plural = ".input {$n :number}\n.match $n\none {{}}\n* {{}}"
    translations = Translation.objects.filter(string=mf2_empty_plural)
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


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0085_remove_entity_word_count"),
    ]
    operations = [
        migrations.RunPython(
            delete_empty_gettext_plurals, reverse_code=migrations.RunPython.noop
        ),
    ]
