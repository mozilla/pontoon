# Generated by Django 4.2.17 on 2024-12-11 19:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0069_notification_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="last_inactive_reminder_sent",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="onboarding_email_status",
            field=models.IntegerField(default=0),
        ),
    ]
