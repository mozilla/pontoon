# Generated by Django 3.2.13 on 2022-08-04 14:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0030_userprofile_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="bio",
            field=models.TextField(blank=True, max_length=160, null=True),
        ),
    ]
