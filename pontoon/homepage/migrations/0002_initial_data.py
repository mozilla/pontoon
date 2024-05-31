# Generated by Django 3.1.3 on 2021-02-25 23:53

from django.db import migrations
from pathlib import Path


def get_homepage_content():
    module_dir = Path(__file__).parent.parent
    file_path = module_dir / "templates/homepage_content.html"
    return file_path.read_text()


def create_homepage_entry(apps, schema_editor):
    Homepage = apps.get_model("homepage", "Homepage")
    if Homepage.objects.count() == 0:
        Homepage.objects.create(text=get_homepage_content(), title="Localize Mozilla")


def remove_homepage_entry(apps, schema_editor):
    Homepage = apps.get_model("homepage", "Homepage")

    try:
        homepage = Homepage.objects.last()
    except Homepage.DoesNotExist:
        return

    homepage.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("homepage", "0001_squashed_0002_add_homepage_content"),
    ]

    operations = [
        migrations.RunPython(
            code=create_homepage_entry,
            reverse_code=remove_homepage_entry,
        ),
    ]
