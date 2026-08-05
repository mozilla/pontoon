from django.db import migrations, models


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
                default=None,
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="userprofile",
            constraint=models.UniqueConstraint(
                models.F("system_user_role"),
                condition=models.Q(("system_user_role__isnull", False)),
                name="base_userprofile_system_user_role_uniq",
            ),
        ),
    ]
