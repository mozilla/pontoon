# Generated by Django 3.2.15 on 2023-10-18 21:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0047_fix_lt_plural_rule"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="theme",
            field=models.CharField(
                choices=[("dark", "Dark"), ("light", "Light"), ("system", "System")],
                default="dark",
                max_length=20,
            ),
        ),
    ]
