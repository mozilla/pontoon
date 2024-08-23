# Generated by Django 4.2.11 on 2024-08-16 10:45

import datetime

from django.db import migrations


def migrate_translation_to_actionlog(apps, schema_editor):
    Translation = apps.get_model("base", "Translation")
    ActionLog = apps.get_model("actionlog", "ActionLog")

    translation_info = {
        "date": ("translation:created", "Translation created"),
        "approved_date": ("translation:approved", "Translation approved"),
        "unapproved_date": ("translation:unapproved", "Translation unapproved"),
        "rejected_date": ("translation:rejected", "Translation rejected"),
        "unrejected_date": ("translation:unrejected", "Translation unrejected"),
    }

    # date to end migration
    end_date = datetime.datetime(
        2020, 1, 7, 9, 25, 11, 829125, tzinfo=datetime.timezone.utc
    )

    actions_to_log = []

    for translation in Translation.objects.filter(date__lt=end_date):
        for attr, action_type in translation_info.items():
            value = getattr(translation, attr)
            if value is not None and value < end_date:
                actions_to_log.append(
                    ActionLog(
                        action_type=action_type,
                        created_at=value,
                        performed_by_id=translation.user_id,
                        translation_id=translation.id,
                    )
                )
    ActionLog.objects.bulk_create(actions_to_log)


class Migration(migrations.Migration):
    dependencies = [
        ("actionlog", "0003_existing_pretranslation_action"),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_translation_to_actionlog,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
