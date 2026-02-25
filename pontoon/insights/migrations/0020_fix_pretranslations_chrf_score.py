from django.db import migrations


def fix_pretranslations_chrf_score(apps, schema_editor):
    """
    Days with no pretranslation reviews were incorrectly stored as 0 instead of
    NULL. Fix by setting all 0 values to NULL so they are excluded from monthly
    averages. Note that this is not 100% accurate, as there may be some days
    with a real 0 score.
    """
    LocaleInsightsSnapshot = apps.get_model("insights", "LocaleInsightsSnapshot")
    ProjectLocaleInsightsSnapshot = apps.get_model(
        "insights", "ProjectLocaleInsightsSnapshot"
    )

    LocaleInsightsSnapshot.objects.filter(pretranslations_chrf_score=0).update(
        pretranslations_chrf_score=None
    )
    ProjectLocaleInsightsSnapshot.objects.filter(pretranslations_chrf_score=0).update(
        pretranslations_chrf_score=None
    )


class Migration(migrations.Migration):
    dependencies = [
        ("insights", "0019_fix_locale_insights_average_suggestion_ages"),
    ]

    operations = [
        migrations.RunPython(
            fix_pretranslations_chrf_score,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
