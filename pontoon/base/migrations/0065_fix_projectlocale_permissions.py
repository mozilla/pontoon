from django.db import migrations

from pontoon.base.signals import assign_group_permissions, create_group


def fix_projectlocale_permissions(apps, schema_editor):
    ProjectLocale = apps.get_model("base", "ProjectLocale")
    for project, locale in [
        ("common-voice", "cdo"),
        ("common-voice", "dar"),
        ("common-voice", "nqo"),
        ("common-voice", "shn"),
        ("firefox-bridge", "de"),
        ("firefox-bridge", "fr"),
        ("firefox-bridge", "it"),
        ("firefox-multi-account-containers", "fur"),
        ("firefox-profiler", "en-CA"),
        ("firefox-profiler", "fur"),
        ("firefox-profiler", "tr"),
    ]:
        try:
            project_locale = ProjectLocale.objects.get(
                project__slug=project, locale__code=locale
            )
            create_group(
                project_locale,
                "translators",
                ["can_translate_project_locale"],
                f"{project}/{locale}",
            )
            assign_group_permissions(
                project_locale, "translators", ["can_translate_project_locale"]
            )
        except ProjectLocale.DoesNotExist:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0064_populate_unique_id"),
    ]

    operations = [
        migrations.RunPython(
            code=fix_projectlocale_permissions,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
