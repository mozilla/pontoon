from django.db import migrations


def reverse_0002_load_initial_data(apps, schema_editor):
    Project = apps.get_model("base", "Project")

    try:
        project = Project.objects.get(slug="pontoon-intro")
        project.delete()
    except Project.DoesNotExist:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0075_fix_android_ini_properties")
    ]

    operations = [
        migrations.RunPython(reverse_0002_load_initial_data),
    ]
