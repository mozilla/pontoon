import django.utils.timezone

from django.db import migrations, models


def use_date_created_as_date_modified(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    projects = Project.objects.all()
    for project in projects:
        project.date_modified = models.F("date_created")
    Project.objects.bulk_update(projects, ["date_modified"])


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0079_trim_android"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="date_modified",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.RunPython(
            code=use_date_created_as_date_modified,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
