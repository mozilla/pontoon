from guardian.conf import settings as guardian_settings

from django.db import migrations


def mark_anonymous_user(apps, schema_editor):
    UserProfile = apps.get_model("base", "UserProfile")
    UserProfile.objects.filter(
        user__username=guardian_settings.ANONYMOUS_USER_NAME
    ).update(system_user=True)


def unmark_anonymous_user(apps, schema_editor):
    UserProfile = apps.get_model("base", "UserProfile")
    UserProfile.objects.filter(
        user__username=guardian_settings.ANONYMOUS_USER_NAME
    ).update(system_user=False)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0137_remove_project_data_source"),
    ]

    operations = [
        migrations.RunPython(mark_anonymous_user, unmark_anonymous_user),
    ]
