from django.db import migrations


def migrate_sync_events(apps, schema_editor):
    Sync = apps.get_model("sync", "Sync")
    ProjectSyncLog = apps.get_model("sync", "ProjectSyncLog")

    sync_events = []
    for prev in ProjectSyncLog.objects.all().prefetch_related("repository_sync_logs"):
        sync = Sync(project=prev.project, start_time=prev.start_time)
        if prev.skipped_end_time:
            sync.status = 99  # Can't differentiate between NO_CHANGES and FAIL
            sync.end_time = prev.skipped_end_time
        else:
            repo_logs = prev.repository_sync_logs.all()
            if repo_logs and all(log.end_time is not None for log in repo_logs):
                sync.status = 1  # Sync.Status.DONE
                sync.end_time = max(log.end_time for log in repo_logs)
        sync_events.append(sync)

    Sync.objects.bulk_create(sync_events, batch_size=10000)


def drop_sync_events(apps, schema_editor):
    Sync = apps.get_model("sync", "Sync")
    Sync.objects.all().delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("sync", "0003_new_sync_events"),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_sync_events,
            reverse_code=drop_sync_events,
        )
    ]
