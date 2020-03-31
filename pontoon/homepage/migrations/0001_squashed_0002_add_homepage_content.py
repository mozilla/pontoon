# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-08 19:28
from __future__ import unicode_literals

import os

from django.db import migrations, models


def get_homepage_content():
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, "../templates/homepage_content.html")
    data_file = open(file_path, "r")
    data = data_file.read()
    return data


def create_homepage_entry(apps, schema_editor):
    Homepage = apps.get_model("homepage", "Homepage")
    homepage = Homepage.objects.create(
        text=get_homepage_content(), title="Localize Mozilla"
    )


def remove_homepage_entry(apps, schema_editor):
    Homepage = apps.get_model("homepage", "Homepage")

    try:
        homepage = Homepage.objects.last()
    except Homepage.DoesNotExist:
        return

    homepage.delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Homepage",
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
                ("text", models.TextField()),
                ("title", models.CharField(default="Pontoon", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RunPython(
            code=create_homepage_entry, reverse_code=remove_homepage_entry,
        ),
    ]
