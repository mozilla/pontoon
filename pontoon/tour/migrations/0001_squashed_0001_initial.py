# Generated by Django 1.11.28 on 2020-03-08 19:25
from django.db import migrations


DEMO_PROJECT_CONTENT = """
Welcome to Pontoon! Translate this sentence and press Enter.
Congratulations, you have translated your first "string"!
Keep translating, we'll show you tips and tricks about Pontoon.
In this sentence, click the dot-dot-dot at the end…
Nice! The "placeable" has been automatically pasted to your translation.
There are <b>different</b> %(types)s of placeables and you usually don't need to translate them.
If a string has a lot of placeables, we have another trick for you.
<strong><a href="%(test)s">Click the Copy button</a> just <em>below</em> the translation input.</strong>
The entire string is copied, and you just translate in-between placeables. Convenient, right?
In the next string, click the Machinery tab.
The quick brown fox jumps over the lazy dog.
Did you see the automatic translation there? If you click a translation in that tab, it gets added to the translation input.
Machinery shows you suggestions from Machine Translation and Translation Memory.
That's all for now. There's a lot more to Pontoon that you'll discover as you use it.
Now go on, grasshopper, and translate to your heart's content!
"""


def create_tutorial_project(apps, schema_editor):
    # Create an empty project
    Project = apps.get_model("base", "Project")
    project, _ = Project.objects.get_or_create(
        slug="tutorial",
        name="Tutorial",
        data_source="database",
        can_be_requested=False,
        sync_disabled=True,
        system_project=True,
        info=(
            "A tutorial project, used as a testing playground and for the guided tour."
        ),
        admin_notes=(
            "Do not remove, this is required in code to show the guided tour."
        ),
    )

    # Add a resource
    Resource = apps.get_model("base", "Resource")
    new_strings = DEMO_PROJECT_CONTENT.strip().split("\n")
    resource, _ = Resource.objects.get_or_create(
        path="playground",
        project=project,
        total_strings=len(new_strings),
    )

    # Add entities
    Entity = apps.get_model("base", "Entity")
    new_entities = [
        Entity(string=new_string, resource=resource, order=index)
        for index, new_string in enumerate(new_strings)
    ]
    Entity.objects.bulk_create(new_entities)

    # Enable project for all localizable locales
    Locale = apps.get_model("base", "Locale")
    ProjectLocale = apps.get_model("base", "ProjectLocale")
    locales = Locale.objects.exclude(code__in=["en-US", "en"])
    project_locales = [
        ProjectLocale(project=project, locale=locale) for locale in locales
    ]
    ProjectLocale.objects.bulk_create(project_locales)

    # Update stats
    TranslatedResource = apps.get_model("base", "TranslatedResource")
    translated_resources = [
        TranslatedResource(
            resource=resource,
            locale=locale,
            total_strings=len(new_strings),
        )
        for locale in locales
    ]
    TranslatedResource.objects.bulk_create(translated_resources)


def remove_tutorial_project(apps, schema_editor):
    Project = apps.get_model("base", "Project")

    try:
        project = Project.objects.get(slug="tutorial")
    except Project.DoesNotExist:
        return

    project.delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("base", "0002_auto_20200322_1821"),
    ]

    operations = [
        migrations.RunPython(
            code=create_tutorial_project,
            reverse_code=remove_tutorial_project,
        ),
    ]
