from django.db import migrations, models


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
    UserProfile.objects.exclude(system_user_role="").update(system_user_role="")


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0124_project_is_chs_project"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="system_user_role",
            field=models.CharField(
                blank=True,
                choices=[
                    ("sync", "Sync"),
                    ("gt", "Google Translate"),
                    ("tm", "Translation Memory"),
                ],
                default="",
                max_length=20,
            ),
        ),
        migrations.RunPython(
            code=set_system_user_roles,
            reverse_code=unset_system_user_roles,
        ),
    ]
