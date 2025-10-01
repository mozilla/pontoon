from datetime import date, datetime, time, timedelta, timezone

from django.db import migrations

from pontoon.insights.tasks import (
    count_activities,
    count_created_entities,
    count_projectlocale_stats,
    locale_insights,
)


def fix_locale_insights(apps, schema_editor):
    LocaleInsightsSnapshot = apps.get_model("insights", "LocaleInsightsSnapshot")

    # https://github.com/mozilla/pontoon/pull/3789 was deployed just after this date
    start_date = date(2025, 9, 24)

    nonempty_dates: set[date] = set(
        LocaleInsightsSnapshot.objects.filter(created_at__gte=start_date)
        .distinct()
        .values_list("created_at", flat=True)
    )
    while start_date in nonempty_dates:
        nonempty_dates.remove(start_date)
        start_date += timedelta(days=1)
    end_date = min(nonempty_dates) if nonempty_dates else date.today()

    pl_stats = count_projectlocale_stats()
    for days in range((end_date - start_date).days):
        d = start_date + timedelta(days=days)
        dt = datetime.combine(d, time(), tzinfo=timezone.utc)
        activities = count_activities(dt)
        new_entities = count_created_entities(dt)
        created = LocaleInsightsSnapshot.objects.bulk_create(
            locale_insights(dt, activities, new_entities, pl_stats)
        )
        print(f" ({d}: {len(created)} snapshots)", end="", flush=True)


class Migration(migrations.Migration):
    dependencies = [("insights", "0017_fix_projectlocale_insights_again")]

    operations = [
        migrations.RunPython(
            fix_locale_insights, reverse_code=migrations.RunPython.noop
        )
    ]
