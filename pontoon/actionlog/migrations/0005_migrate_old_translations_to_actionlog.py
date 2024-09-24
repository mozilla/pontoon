# Generated by Django 4.2.11 on 2024-09-24 17:56

import datetime

from django.db import migrations


def migrate_translations_to_actionlog(apps, schema_editor):
    Translation = apps.get_model("base", "Translation")
    ActionLog = apps.get_model("actionlog", "ActionLog")

    translation_info = {
        "date": (
            "translation:created",
            "user",
        ),
        "approved_date": (
            "translation:approved",
            "approved_user",
        ),
        "unapproved_date": (
            "translation:unapproved",
            "unapproved_user",
        ),
        "rejected_date": (
            "translation:rejected",
            "rejected_user",
        ),
        "unrejected_date": (
            "translation:unrejected",
            "unrejected_user",
        ),
    }

    # Timestamp of the first Translation created after the introduction of ActionLog
    end_date = datetime.datetime(
        2020, 1, 7, 9, 25, 11, 829125, tzinfo=datetime.timezone.utc
    )

    actions_to_log = []

    BATCH_SIZE = 10000

    # To improve performance:
    #  - Exclude translations that don't have any user set
    #  - Filter only the necessary fields
    translations = (
        Translation.objects.filter(date__lt=end_date)
        .exclude(
            user=None,
            approved_user=None,
            unapproved_user=None,
            rejected_user=None,
            unrejected_user=None,
        )
        .values(
            "id",
            "date",
            "approved_date",
            "unapproved_date",
            "rejected_date",
            "unrejected_date",
            "user",
            "approved_user",
            "unapproved_user",
            "rejected_user",
            "unrejected_user",
        )
    ).iterator(chunk_size=BATCH_SIZE)

    for translation in translations:
        for action_date, (action_type, action_user) in translation_info.items():
            date = translation.get(action_date)
            user_id = translation.get(action_user)

            # Do not log Approve actions for self-approved translations
            if action_type == "translation:approved" and date == translation.get(
                "date"
            ):
                continue

            # Only log actions if the date is before the end_date, and user_id is set
            if date is not None and date < end_date and user_id is not None:
                actions_to_log.append(
                    ActionLog(
                        action_type=action_type,
                        created_at=date,
                        performed_by_id=user_id,
                        translation_id=translation.get("id"),
                    )
                )

    ActionLog.objects.bulk_create(actions_to_log, batch_size=BATCH_SIZE)


class Migration(migrations.Migration):
    dependencies = [
        ("actionlog", "0004_alter_actionlog_created_at"),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_translations_to_actionlog,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
