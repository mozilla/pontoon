# Generated by Django 2.2.13 on 2020-07-23 19:29

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0007_machinery_sources_translation"),
    ]

    operations = [
        migrations.AddField(
            model_name="locale",
            name="systran_translate_code",
            field=models.CharField(
                blank=True,
                help_text='\n        SYSTRAN maintains its own list of\n        <a href="https://platform.systran.net/index">supported locales</a>.\n        Choose a matching locale from the list or leave blank to disable\n        support for SYSTRAN machine translation service.\n        ',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="locale",
            name="systran_translate_profile",
            field=models.CharField(
                blank=True,
                help_text="\n        SYSTRAN Profile UUID to specify the engine trained on the en-locale language pair.\n        The field is updated automatically after the systran_translate_code field changes.\n        ",
                max_length=128,
            ),
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
                        ("transvision", "Mozilla"),
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
