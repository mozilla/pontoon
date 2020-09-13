# Generated by Django 2.2.13 on 2020-10-10 22:57

from django.db import migrations


def make_tutorial_public(apps, schema_editor):
    """Tutorial should be public by default."""

    Project = apps.get_model("base", "Project")
    Project.objects.filter(slug="tutorial").update(visibility="public")


class Migration(migrations.Migration):

    dependencies = [
        ("tour", "0001_squashed_0001_initial"),
    ]

    operations = [migrations.RunPython(make_tutorial_public, migrations.RunPython.noop)]
