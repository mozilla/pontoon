from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0139_userprofile_machinery_autocomplete"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="machinery_autocomplete",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="machinery_autocomplete",
            field=models.CharField(
                choices=[
                    ("off", "Off"),
                    ("word", "Word by word"),
                    ("full", "Full continuation"),
                ],
                max_length=20,
                null=True,
                blank=True,
                default=None,
            ),
        ),
    ]
