from datetime import timedelta

from django.db import migrations
from django.db.migrations.recorder import MigrationRecorder


REJECTED = "translation:rejected"
TRIGGER_TYPES = ("translation:created", "translation:approved")

# Smallest gap among any explicit rejection is 1089ms, hence the 1000ms window
TRIGGER_WINDOW = timedelta(milliseconds=1000)

BATCH_SIZE = 10000


def flag_live_since(connection):
    return (
        MigrationRecorder(connection)
        .migration_qs.get(app="actionlog", name="0007_actionlog_is_implicit_action")
        .applied
    )


def backfill_is_implicit_action(apps, schema_editor):
    ActionLog = apps.get_model("actionlog", "ActionLog")
    cutoff = flag_live_since(schema_editor.connection)

    old_rejections = ActionLog.objects.filter(
        action_type=REJECTED,
        created_at__lt=cutoff,
        performed_by__isnull=False,
    )

    old_rejections.filter(performed_by__profile__system_user=True).update(
        is_implicit_action=True
    )
    old_rejections = old_rejections.exclude(performed_by__profile__system_user=True)

    performer_ids = list(
        old_rejections.order_by().values_list("performed_by_id", flat=True).distinct()
    )

    implicit_ids = []

    def flush():
        ActionLog.objects.filter(id__in=implicit_ids).update(is_implicit_action=True)
        implicit_ids.clear()

    for performer_id in performer_ids:
        rejections = (
            old_rejections.filter(performed_by_id=performer_id)
            .order_by("created_at")
            .values_list("id", "created_at")
            .iterator(chunk_size=BATCH_SIZE)
        )
        triggers = (
            ActionLog.objects.filter(
                performed_by_id=performer_id,
                action_type__in=TRIGGER_TYPES,
                created_at__lt=cutoff + TRIGGER_WINDOW,
            )
            .order_by("created_at")
            .values_list("created_at", flat=True)
            .iterator(chunk_size=BATCH_SIZE)
        )

        trigger = next(triggers, None)
        for action_id, rejected_at in rejections:
            while trigger is not None and trigger < rejected_at:
                trigger = next(triggers, None)
            if trigger is not None and trigger <= rejected_at + TRIGGER_WINDOW:
                implicit_ids.append(action_id)
                if len(implicit_ids) >= BATCH_SIZE:
                    flush()

    if implicit_ids:
        flush()


def clear_is_implicit_action(apps, schema_editor):
    ActionLog = apps.get_model("actionlog", "ActionLog")
    cutoff = flag_live_since(schema_editor.connection)

    ActionLog.objects.filter(
        action_type=REJECTED,
        created_at__lt=cutoff,
        is_implicit_action=True,
    ).update(is_implicit_action=False)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("actionlog", "0007_actionlog_is_implicit_action"),
        ("base", "0039_mark_system_users"),
    ]

    operations = [
        migrations.RunPython(
            code=backfill_is_implicit_action,
            reverse_code=clear_is_implicit_action,
        ),
    ]
