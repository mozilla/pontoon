# Generated by Django 3.1.3 on 2020-12-23 15:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0012_auto_20201020_1830"),
        ("insights", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectLocaleInsightsSnapshot",
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
                ("total_strings", models.PositiveIntegerField(default=0)),
                ("approved_strings", models.PositiveIntegerField(default=0)),
                ("fuzzy_strings", models.PositiveIntegerField(default=0)),
                ("strings_with_errors", models.PositiveIntegerField(default=0)),
                ("strings_with_warnings", models.PositiveIntegerField(default=0)),
                ("unreviewed_strings", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateField(default=django.utils.timezone.now)),
                ("completion", models.FloatField()),
                (
                    "project_locale",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="base.projectlocale",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="ProjectInsightsSnapshot",
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
                ("total_strings", models.PositiveIntegerField(default=0)),
                ("approved_strings", models.PositiveIntegerField(default=0)),
                ("fuzzy_strings", models.PositiveIntegerField(default=0)),
                ("strings_with_errors", models.PositiveIntegerField(default=0)),
                ("strings_with_warnings", models.PositiveIntegerField(default=0)),
                ("unreviewed_strings", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateField(default=django.utils.timezone.now)),
                ("completion", models.FloatField()),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="base.project"
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
    ]
