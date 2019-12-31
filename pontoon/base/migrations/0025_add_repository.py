# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0024_locale_team_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="Repository",
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
                (
                    "type",
                    models.CharField(
                        default=b"file",
                        max_length=255,
                        choices=[
                            (b"file", b"File"),
                            (b"git", b"Git"),
                            (b"hg", b"HG"),
                            (b"svn", b"SVN"),
                            (b"transifex", b"Transifex"),
                        ],
                    ),
                ),
                (
                    "url",
                    models.CharField(max_length=2000, verbose_name=b"URL", blank=True),
                ),
                ("project", models.ForeignKey(to="base.Project")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.AlterUniqueTogether(
            name="repository", unique_together=set([("project", "url")]),
        ),
    ]
