import logging

from django.db import migrations


log = logging.getLogger(__name__)


def remove_db_project_repositories(apps, schema_editor):
    """
    Projects without repositories are now treated as DB projects. The admin form
    allowed saving repositories for DB projects, which would make them syncable.
    """
    Repository = apps.get_model("base", "Repository")
    repositories = Repository.objects.filter(project__data_source="database")
    for slug in repositories.values_list("project__slug", flat=True).distinct():
        log.warning(f"Removing repositories of DB project {slug}")
    repositories.delete()


def restore_data_source(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    Project.objects.filter(repositories__isnull=True).update(data_source="database")


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0135_fix_fluent_function_names"),
        # Creates the Tutorial project with data_source set.
        ("tour", "0001_squashed_0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            remove_db_project_repositories, reverse_code=restore_data_source
        ),
    ]
