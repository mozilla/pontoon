# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0044_locale_translators"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectSyncLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("start_time", models.DateTimeField(default=django.utils.timezone.now)),
                ("project", models.ForeignKey(to="base.Project")),
            ],
        ),
        migrations.CreateModel(
            name="RepositorySyncLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("start_time", models.DateTimeField(default=django.utils.timezone.now)),
                ("end_time", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "project_sync_log",
                    models.ForeignKey(
                        related_name="repository_sync_logs", to="sync.ProjectSyncLog"
                    ),
                ),
                ("repository", models.ForeignKey(to="base.Repository")),
            ],
        ),
        migrations.CreateModel(
            name="SyncLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("start_time", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name="projectsynclog",
            name="sync_log",
            field=models.ForeignKey(
                related_name="project_sync_logs", to="sync.SyncLog"
            ),
        ),
    ]
