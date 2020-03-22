# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-22 18:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0001_squashed_0154_auto_20200206_1736"),
    ]

    operations = [
        migrations.AlterField(
            model_name="permissionchangelog",
            name="performed_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="changed_permissions_log",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="permissionchangelog",
            name="performed_on",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="permisions_log",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="contact",
            field=models.ForeignKey(
                blank=True,
                help_text="\n        L10n driver in charge of the project\n    ",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="contact_for",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="translation",
            name="approved_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="approved_translations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="translation",
            name="rejected_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rejected_translations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="translation",
            name="unapproved_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="unapproved_translations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="translation",
            name="unrejected_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="unrejected_translations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="translation",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RemoveIndex(
            model_name="translation", name="base_transl_entity__fbea1e_partial",
        ),
        migrations.RemoveIndex(
            model_name="translation", name="base_transl_entity__ed9592_partial",
        ),
        migrations.AddConstraint(
            model_name="translation",
            constraint=models.UniqueConstraint(
                condition=models.Q(active=True),
                fields=("entity", "locale", "plural_form", "active"),
                name="entity_locale_plural_form_active",
            ),
        ),
        migrations.AddConstraint(
            model_name="translation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("active", True), ("plural_form__isnull", True)),
                fields=("entity", "locale", "active"),
                name="entity_locale_active",
            ),
        ),
    ]
