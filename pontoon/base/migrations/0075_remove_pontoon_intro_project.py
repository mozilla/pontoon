from django.db import migrations


def reverse_0002_load_initial_data(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    Repository = apps.get_model("base", "Repository")

    try:
        project = Project.objects.get(slug="pontoon-intro")
        project.delete()
    except Project.DoesNotExist:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0074_remove_repository_permalink_prefix"),  # update as needed
    ]

    operations = [
        migrations.RunPython(reverse_0002_load_initial_data),
    ]
