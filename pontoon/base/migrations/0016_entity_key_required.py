# Generated by Django 3.2.4 on 2021-08-19 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0015_userprofile_has_dismissed_addon_promotion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entity",
            name="key",
            field=models.TextField(),
        ),
    ]
