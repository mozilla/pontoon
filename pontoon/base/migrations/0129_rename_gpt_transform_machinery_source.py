from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models
from django.db.models import F, Func, Value


OLD = "gpt-transform"
NEW = "openai-chatgpt"


class ArrayReplace(Func):
    """Postgres `array_replace`, swapping one element of an array for another.

    Lets the rename run as a single UPDATE, and keeps the other sources on a
    translation — and their order — untouched.
    """

    function = "array_replace"
    arity = 3
    output_field = ArrayField(models.CharField(max_length=30))


def replace_source(apps, old, new):
    Translation = apps.get_model("base", "Translation")
    Translation.objects.filter(machinery_sources__contains=[old]).update(
        machinery_sources=ArrayReplace(F("machinery_sources"), Value(old), Value(new))
    )


def rename_forwards(apps, schema_editor):
    replace_source(apps, OLD, NEW)


def rename_backwards(apps, schema_editor):
    replace_source(apps, NEW, OLD)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0128_alter_translation_machinery_sources"),
    ]

    operations = [
        migrations.RunPython(rename_forwards, rename_backwards),
    ]
