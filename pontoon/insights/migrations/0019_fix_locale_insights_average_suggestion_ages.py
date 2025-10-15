from datetime import date, timedelta

from django.db import migrations


def fix_locale_insights_average_suggestion_ages(apps, schema_editor):
    LocaleInsightsSnapshot = apps.get_model("insights", "LocaleInsightsSnapshot")

    # https://github.com/mozilla/pontoon/pull/3789 was merged just after this date
    min_date = date(2025, 9, 24)

    # We were using seconds as days, so multiplying values by 86400.
    # This matches an actual average age of about 1 hour.
    min_bad_age = timedelta(days=3650)

    try:
        start_date = (
            LocaleInsightsSnapshot.objects.filter(
                created_at__gte=min_date,
                unreviewed_suggestions_lifespan__gt=min_bad_age,
            )
            .order_by("created_at")[0]
            .created_at
        )
    except IndexError:
        # There might not be any bad data to fix.
        print(" (nothing to fix)", end="", flush=True)
        return

    print(f" (fixing from {start_date} onwards)", end="", flush=True)
    snapshots = LocaleInsightsSnapshot.objects.filter(created_at__gte=start_date)
    for s in snapshots:
        s.unreviewed_suggestions_lifespan /= 86400
    LocaleInsightsSnapshot.objects.bulk_update(
        snapshots, ["unreviewed_suggestions_lifespan"]
    )


class Migration(migrations.Migration):
    dependencies = [("insights", "0018_fix_locale_insights")]

    operations = [
        migrations.RunPython(
            fix_locale_insights_average_suggestion_ages,
            reverse_code=migrations.RunPython.noop,
        )
    ]
