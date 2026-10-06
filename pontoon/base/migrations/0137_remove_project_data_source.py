from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0136_remove_db_project_repositories"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="data_source",
        ),
    ]
