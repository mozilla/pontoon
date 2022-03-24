# Generated by Django 3.2.10 on 2022-03-24 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("insights", "0009_fix_projectlocale_insights_data"),
    ]

    operations = [
        migrations.RenameField(
            model_name="localeinsightssnapshot",
            old_name="fuzzy_strings",
            new_name="pretranslated_strings",
        ),
        migrations.RenameField(
            model_name="projectinsightssnapshot",
            old_name="fuzzy_strings",
            new_name="pretranslated_strings",
        ),
        migrations.RenameField(
            model_name="projectlocaleinsightssnapshot",
            old_name="fuzzy_strings",
            new_name="pretranslated_strings",
        ),
    ]
