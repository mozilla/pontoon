# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0041_create_locale_permissions"),
    ]

    operations = [
        migrations.AddField(
            "Locale",
            "translators_group",
            models.ForeignKey(
                to="auth.Group",
                null=True,
                related_name="translated_locales",
                on_delete=models.SET_NULL,
            ),
        ),
        migrations.AddField(
            "Locale",
            "managers_group",
            models.ForeignKey(
                to="auth.Group",
                null=True,
                related_name="managed_locales",
                on_delete=models.SET_NULL,
            ),
        ),
    ]
