from django.db import migrations


# Match both email variants, just in case something went wrong
# with previous migrations.
system_user_roles = {
    "pontoon-sync@example.com": "sync",
    "pontoon-sync@mozilla.com": "sync",
    "pontoon-gt@example.com": "gt",
    "pontoon-gt@mozilla.com": "gt",
    "pontoon-tm@example.com": "tm",
    "pontoon-tm@mozilla.com": "tm",
}


def set_system_user_roles(apps, schema_editor):
    UserProfile = apps.get_model("base", "UserProfile")
    for email, role in system_user_roles.items():
        UserProfile.objects.filter(user__email=email).update(
            system_user=True, system_user_role=role
        )


def unset_system_user_roles(apps, schema_editor):
    UserProfile = apps.get_model("base", "UserProfile")
    UserProfile.objects.exclude(system_user_role=None).update(system_user_role=None)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0125_userprofile_system_user_role"),
        # Ensures the sync user exists before we try to give it a role.
        ("sync", "0002_change_pontoon_sync_email"),
    ]

    operations = [
        migrations.RunPython(
            code=set_system_user_roles,
            reverse_code=unset_system_user_roles,
        ),
    ]
