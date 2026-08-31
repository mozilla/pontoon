from django.db import migrations


CLDR_PLURALS = ("zero", "one", "two", "few", "many", "other")


def plural_categories(cldr_plurals: str) -> list[str]:
    """Matches Locale.cldr_plurals_list(), which is unavailable to migrations."""
    if cldr_plurals == "":
        return ["other"]
    res: list[str] = []
    for p in cldr_plurals.split(","):
        try:
            res.append(CLDR_PLURALS[int(p)])
        except (ValueError, IndexError):
            pass
    return res


def fix_plural_catchall(apps, schema_editor):
    """Label the catchall variant of gettext plurals with the locale's own category.

    gettext addresses plural forms by category, so a catchall labelled `other`
    in a locale whose categories are `one, few, many` matches no form and is
    serialized as an empty msgstr. Only gettext is affected.
    """
    Locale = apps.get_model("base", "Locale")
    Translation = apps.get_model("base", "Translation")

    catchalls = {}

    for pk, cldr_plurals in Locale.objects.values_list("pk", "cldr_plurals"):
        categories = plural_categories(cldr_plurals)
        if len(categories) > 1 and categories[-1] != "other":
            catchalls[pk] = categories[-1]

    if not catchalls:
        return

    updates = []
    translations = Translation.objects.filter(
        locale_id__in=catchalls,
        entity__resource__format="gettext",
        value__has_key="alt",
    ).iterator()

    for tx in translations:
        catchall = catchalls[tx.locale_id]
        changed = False

        for variant in tx.value["alt"]:
            for i, key in enumerate(variant["keys"]):
                if isinstance(key, dict) and key.get("*") != catchall:
                    variant["keys"][i] = {"*": catchall}
                    changed = True

        if changed:
            updates.append(tx)

    print(
        f"\n    Re-labelling plural catchalls in {len(updates)} translations"
        f" across {len(catchalls)} locales...\n   ",
        end="",
        flush=True,
    )
    Translation.objects.bulk_update(updates, ["value"], batch_size=10_000)


class Migration(migrations.Migration):
    dependencies = [("base", "0130_userprofile_monthly_health_report")]

    operations = [
        migrations.RunPython(
            fix_plural_catchall, reverse_code=migrations.RunPython.noop
        ),
    ]
