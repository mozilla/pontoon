from django.db import migrations, models


def set_format(apps, schema_editor):
    Resource = apps.get_model("base", "Resource")
    resources = Resource.objects.filter(format__in={"ftl", "json", "po", "xlf", "xml"})
    for res in resources:
        match res.format:
            case "ftl":
                res.format = "fluent"
            case "json":
                res.format = (
                    "webext" if res.path.endswith("messages.json") else "plain_json"
                )
            case "po":
                res.format = "gettext"
            case "xlf":
                res.format = "xliff"
            case "xml":
                res.format = "android"
    Resource.objects.bulk_update(resources, ["format"], batch_size=10_000)


def unset_format(apps, schema_editor):
    Resource = apps.get_model("base", "Resource")
    resources = Resource.objects.filter(
        format__in={"android", "fluent", "gettext", "plain_json", "webext", "xcode"}
    )
    for res in resources:
        match res.format:
            case "fluent":
                res.format = "ftl"
            case "plain_json" | "webext":
                res.format = "json"
            case "gettext":
                res.format = "po"
            case "android":
                res.format = "xml"
            case "xcode":
                res.format = "xliff"
    Resource.objects.bulk_update(resources, ["format"], batch_size=10_000)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0093_remove_entity_source"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resource",
            name="format",
            field=models.CharField(
                blank=True,
                choices=[
                    ("android", "android"),
                    ("dtd", "dtd"),
                    ("fluent", "fluent"),
                    ("gettext", "gettext"),
                    ("ini", "ini"),
                    ("plain_json", "plain_json"),
                    ("properties", "properties"),
                    ("webext", "webext"),
                    ("xcode", "xcode"),
                    ("xliff", "xliff"),
                ],
                max_length=20,
                verbose_name="Format",
            ),
        ),
        migrations.RunPython(set_format, reverse_code=unset_format),
    ]
