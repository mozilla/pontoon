# Generated by Django 3.1.3 on 2021-02-03 14:15

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0012_auto_20201020_1830"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="locale",
            name="transvision",
        ),
        migrations.AlterField(
            model_name="translation",
            name="machinery_sources",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("translation-memory", "Translation Memory"),
                        ("google-translate", "Google Translate"),
                        ("microsoft-translator", "Microsoft Translator"),
                        ("systran-translate", "Systran Translate"),
                        ("microsoft-terminology", "Microsoft"),
                        ("caighdean", "Caighdean"),
                    ],
                    max_length=30,
                ),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
