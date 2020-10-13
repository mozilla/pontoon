# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-08 19:52
from django.db import migrations, models
import django.db.migrations.operations.special
import django.db.models.deletion


def remove_warnings_and_errors(apps, schema_editor):
    """
    Remove all warnings and errors related to Translate Toolkit.
    """
    Warning = apps.get_model("checks", "Warning")
    Error = apps.get_model("checks", "Error")

    Warning.objects.filter(library="tt").delete()
    Error.objects.filter(library="tt").delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("base", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Error",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "library",
                    models.CharField(
                        choices=[
                            (b"p", b"pontoon"),
                            (b"tt", b"translate-toolkit"),
                            (b"cl", b"compare-locales"),
                        ],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                ("message", models.TextField()),
                (
                    "translation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="errors",
                        to="base.Translation",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="Warning",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "library",
                    models.CharField(
                        choices=[
                            (b"p", b"pontoon"),
                            (b"tt", b"translate-toolkit"),
                            (b"cl", b"compare-locales"),
                        ],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                ("message", models.TextField()),
                (
                    "translation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="warnings",
                        to="base.Translation",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.AlterUniqueTogether(
            name="warning",
            unique_together=set([("translation", "library", "message")]),
        ),
        migrations.AlterUniqueTogether(
            name="error", unique_together=set([("translation", "library", "message")]),
        ),
        migrations.RunPython(
            code=remove_warnings_and_errors,
            reverse_code=django.db.migrations.operations.special.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="error",
            name="library",
            field=models.CharField(
                choices=[(b"p", b"pontoon"), (b"cl", b"compare-locales")],
                db_index=True,
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="warning",
            name="library",
            field=models.CharField(
                choices=[(b"p", b"pontoon"), (b"cl", b"compare-locales")],
                db_index=True,
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="error",
            name="library",
            field=models.CharField(
                choices=[("p", "pontoon"), ("cl", "compare-locales")],
                db_index=True,
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="warning",
            name="library",
            field=models.CharField(
                choices=[("p", "pontoon"), ("cl", "compare-locales")],
                db_index=True,
                max_length=20,
            ),
        ),
    ]
