# Generated by Django 4.2.16 on 2024-12-10 19:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("actionlog", "0006_actionlog_tm_entries_alter_actionlog_action_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="actionlog",
            name="is_implicit_action",
            field=models.BooleanField(default=False),
        ),
    ]