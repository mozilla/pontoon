from django.db import migrations


def fix_gettext_plural_forms(apps, schema_editor):
    Translation = apps.get_model("base", "Translation")
    broken = Translation.objects.filter(plural_form__isnull=True).exclude(
        entity__string_plural=""
    )
    broken.update(plural_form=0)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0048_userprofile_theme"),
    ]

    operations = [
        migrations.RunPython(
            code=fix_gettext_plural_forms,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
