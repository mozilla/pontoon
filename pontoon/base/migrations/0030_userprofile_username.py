# Generated by Django 3.2.13 on 2022-08-04 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0029_external_accounts"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="username",
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
