from datetime import date, datetime, time, timedelta, timezone
from statistics import mean

from django.db import migrations

from pontoon.insights.tasks import count_activities


def fix_projectlocale_insights_again(apps, schema_editor):
    ProjectLocaleInsightsSnapshot = apps.get_model(
        "insights", "ProjectLocaleInsightsSnapshot"
    )

    # https://github.com/mozilla/pontoon/pull/3536 was deployed just after this date
    start_date = date(2025, 1, 21)

    nonempty_dates: set[date] = set(
        ProjectLocaleInsightsSnapshot.objects.filter(created_at__gte=start_date)
        .exclude(
            human_translations=0,
            machinery_translations=0,
            peer_approved=0,
            self_approved=0,
            rejected=0,
            new_suggestions=0,
            pretranslations_approved=0,
            pretranslations_rejected=0,
            pretranslations_new=0,
        )
        .distinct()
        .values_list("created_at", flat=True)
    )
    while start_date in nonempty_dates:
        nonempty_dates.remove(start_date)
        start_date += timedelta(days=1)
    end_date = min(nonempty_dates) if nonempty_dates else date.today()

    prev_date = None
    for days in range((end_date - start_date).days):
        d = start_date + timedelta(days=days)
        dt = datetime.combine(d, time(), tzinfo=timezone.utc)
        activities = count_activities(dt)
        pls_list = [
            pls
            for pls in ProjectLocaleInsightsSnapshot.objects.filter(created_at=d)
            if pls.project_locale_id in activities
        ]
        for pls in pls_list:
            ad = activities[pls.project_locale_id]
            pls.human_translations = len(ad.human_translations)
            pls.machinery_translations = len(ad.machinery_translations)
            pls.peer_approved = len(ad.peer_approved)
            pls.self_approved = len(ad.self_approved)
            pls.rejected = len(ad.rejected)
            pls.new_suggestions = len(ad.new_suggestions)
            if ad.pretranslations_chrf_scores:
                pls.pretranslations_chrf_score = mean(ad.pretranslations_chrf_scores)
            pls.pretranslations_approved = len(ad.pretranslations_approved)
            pls.pretranslations_rejected = len(ad.pretranslations_rejected)
            pls.pretranslations_new = len(ad.pretranslations_new)
        ProjectLocaleInsightsSnapshot.objects.bulk_update(
            pls_list,
            [
                "human_translations",
                "machinery_translations",
                "peer_approved",
                "self_approved",
                "rejected",
                "new_suggestions",
                "pretranslations_chrf_score",
                "pretranslations_approved",
                "pretranslations_rejected",
                "pretranslations_new",
            ],
        )
        if prev_date is None or d.month != prev_date.month:
            print(f" ({d.year}-{d.month:02d})", end="", flush=True)
        prev_date = d


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0009_change_pontoon_users_emails"),
        ("insights", "0016_delete_projectinsightssnapshot"),
    ]

    operations = [
        migrations.RunPython(
            fix_projectlocale_insights_again, reverse_code=migrations.RunPython.noop
        ),
    ]
