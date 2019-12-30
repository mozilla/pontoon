# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0013_add_en_US"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChangedEntityLocale",
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
                ("entity", models.ForeignKey(to="base.Entity")),
                ("locale", models.ForeignKey(to="base.Locale")),
            ],
        ),
        migrations.AddField(
            model_name="entity",
            name="changed_locales",
            field=models.ManyToManyField(
                help_text=b"List of locales in which translations for this entity have changed since the last sync.",
                to="base.Locale",
                through="base.ChangedEntityLocale",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="changedentitylocale", unique_together=set([("entity", "locale")]),
        ),
    ]
