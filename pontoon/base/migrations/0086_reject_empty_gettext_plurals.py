from django.db import migrations
from django.utils import timezone


def reject_empty_gettext_plurals(apps, schema_editor):
    ActionLog = apps.get_model("actionlog", "ActionLog")
    User = apps.get_model("auth", "User")
    Translation = apps.get_model("base", "Translation")

    now = timezone.now()
    sync_user = User.objects.get(username="pontoon-sync")

    mf2_empty_plural = ".input {$n :number}\n.match $n\none {{}}\n* {{}}"
    translations = Translation.objects.filter(string=mf2_empty_plural, approved=True)
    for t in translations:
        t.active = False
        t.approved = False
        t.rejected = True
        t.rejected_date = now
        t.rejected_user = sync_user
    actions = [
        ActionLog(
            action_type="translation:rejected",
            created_at=now,
            performed_by=sync_user,
            translation=t,
        )
        for t in translations
    ]

    Translation.objects.bulk_update(
        translations,
        ["active", "approved", "rejected", "rejected_date", "rejected_user"],
    )
    ActionLog.objects.bulk_create(actions)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0085_remove_entity_word_count"),
    ]
    operations = [
        migrations.RunPython(
            reject_empty_gettext_plurals, reverse_code=migrations.RunPython.noop
        ),
    ]
