import json

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth
from django.db.models import Avg, Count, Q, Sum

from pontoon.base.utils import convert_to_unix_time
from pontoon.insights.models import (
    LocaleInsightsSnapshot,
    ProjectLocaleInsightsSnapshot,
    active_users_default,
)


def get_insight_start_date():
    """Include at most the last year of data in insights."""
    now = datetime.now()
    if now.month == 12:
        return datetime(now.year, 1, 1)
    return datetime(now.year - 1, now.month + 1, 1)


def get_time_to_review(time_to_review):
    if not time_to_review:
        return None

    return round(time_to_review.total_seconds() / 86400, 2)


def get_time_to_review_12_month_avg(category, query_filters=None):
    """For each month, get the average age of suggestions or pretranslations reviewed
    in the 12 months before each month.
    """
    snapshots = LocaleInsightsSnapshot.objects.filter(
        created_at__gte=datetime.now() - relativedelta(years=2)
    )

    if query_filters:
        snapshots = snapshots.filter(query_filters)

    insights = (
        snapshots
        # Truncate to month and add to select list
        .annotate(month=TruncMonth("created_at"))
        # Group By month
        .values("month")
        # Select the avg of the grouping
        .annotate(
            **{
                f"time_to_review_{category}_avg": Avg(
                    f"time_to_review_{category}",
                    filter=Q(**{f"time_to_review_{category}__isnull": False}),
                )
            }
        )
        # Select month and values
        .values(
            "month",
            f"time_to_review_{category}_avg",
        ).order_by("month")
    )

    times_to_review = [x[f"time_to_review_{category}_avg"] for x in insights]
    reversed_times_to_review = list(reversed(times_to_review))
    times_to_review_12_month_avg = []

    for i, time in enumerate(reversed_times_to_review):
        if len(times_to_review_12_month_avg) == 12:
            break

        try:
            previous_12_months = reversed_times_to_review[(i + 1) : (i + 13)]
        except KeyError:
            break

        previous_12_months = [i for i in previous_12_months if i is not None]
        if previous_12_months:
            average = sum(previous_12_months, timedelta()) / len(previous_12_months)
            value = round(average.total_seconds() / 86400, 2)
        else:
            value = None
        times_to_review_12_month_avg.insert(0, value)

    return json.dumps(times_to_review_12_month_avg)


def get_locale_insights(query_filters=None):
    """Get data required by the Locale Insights tab.

    :param django.db.models.Q query_filters: filters insights by given query_filters.

    TODO: Refactor as get_insights(locale, project)
    """
    start_date = get_insight_start_date()
    snapshots = LocaleInsightsSnapshot.objects.filter(created_at__gte=start_date)

    if query_filters:
        snapshots = snapshots.filter(query_filters)

    insights = (
        snapshots
        # Truncate to month and add to select list
        .annotate(month=TruncMonth("created_at"))
        # Group By month
        .values("month")
        # Select the avg/sum of the grouping
        .annotate(unreviewed_lifespan_avg=Avg("unreviewed_suggestions_lifespan"))
        .annotate(
            time_to_review_suggestions_avg=Avg(
                "time_to_review_suggestions",
                filter=Q(time_to_review_suggestions__isnull=False),
            )
        )
        .annotate(
            time_to_review_pretranslations_avg=Avg(
                "time_to_review_pretranslations",
                filter=Q(time_to_review_pretranslations__isnull=False),
            )
        )
        .annotate(completion_avg=Avg("completion"))
        .annotate(human_translations_sum=Sum("human_translations"))
        .annotate(machinery_sum=Sum("machinery_translations"))
        .annotate(new_source_strings_sum=Sum("new_source_strings"))
        .annotate(unreviewed_avg=Avg("unreviewed_strings"))
        .annotate(peer_approved_sum=Sum("peer_approved"))
        .annotate(self_approved_sum=Sum("self_approved"))
        .annotate(rejected_sum=Sum("rejected"))
        .annotate(new_suggestions_sum=Sum("new_suggestions"))
        # Select month and values
        .values(
            "month",
            "unreviewed_lifespan_avg",
            "time_to_review_suggestions_avg",
            "time_to_review_pretranslations_avg",
            "completion_avg",
            "human_translations_sum",
            "machinery_sum",
            "new_source_strings_sum",
            "unreviewed_avg",
            "peer_approved_sum",
            "self_approved_sum",
            "rejected_sum",
            "new_suggestions_sum",
        )
        .order_by("month")
    )

    output = {}
    latest = snapshots.latest("created_at") if snapshots else None

    if latest:
        output.update(
            {
                "total_users": {
                    "managers": latest.total_managers,
                    "reviewers": latest.total_reviewers,
                    "contributors": latest.total_contributors,
                },
                "active_users_last_month": latest.active_users_last_month,
                "active_users_last_3_months": latest.active_users_last_3_months,
                "active_users_last_6_months": latest.active_users_last_6_months,
                "active_users_last_12_months": latest.active_users_last_12_months,
            }
        )
    else:
        output.update(
            {
                "total_users": active_users_default(),
                "active_users_last_month": active_users_default(),
                "active_users_last_3_months": active_users_default(),
                "active_users_last_6_months": active_users_default(),
                "active_users_last_12_months": active_users_default(),
            }
        )

    output.update(
        {
            "dates": [convert_to_unix_time(x["month"]) for x in insights],
            "unreviewed_lifespans": [
                x["unreviewed_lifespan_avg"].days for x in insights
            ],
            "time_to_review_suggestions": json.dumps(
                [
                    get_time_to_review(x["time_to_review_suggestions_avg"])
                    for x in insights
                ]
            ),
            "time_to_review_suggestions_12_month_avg": get_time_to_review_12_month_avg(
                "suggestions", query_filters
            ),
            "time_to_review_pretranslations": json.dumps(
                [
                    get_time_to_review(x["time_to_review_pretranslations_avg"])
                    for x in insights
                ]
            ),
            "time_to_review_pretranslations_12_month_avg": get_time_to_review_12_month_avg(
                "pretranslations", query_filters
            ),
            "translation_activity": {
                "completion": [round(x["completion_avg"], 2) for x in insights],
                "human_translations": [x["human_translations_sum"] for x in insights],
                "machinery_translations": [x["machinery_sum"] for x in insights],
                "new_source_strings": [x["new_source_strings_sum"] for x in insights],
            },
            "review_activity": {
                "unreviewed": [int(round(x["unreviewed_avg"])) for x in insights],
                "peer_approved": [x["peer_approved_sum"] for x in insights],
                "self_approved": [x["self_approved_sum"] for x in insights],
                "rejected": [x["rejected_sum"] for x in insights],
                "new_suggestions": [x["new_suggestions_sum"] for x in insights],
            },
        }
    )

    return output


def get_insights(locale=None, project=None):
    """Get data required by the Insights tab."""
    start_date = get_insight_start_date()
    snapshots = ProjectLocaleInsightsSnapshot.objects.filter(created_at__gte=start_date)

    if locale:
        snapshots = snapshots.filter(project_locale__locale=locale)

    if project:
        snapshots = snapshots.filter(project_locale__project=project)

    insights = (
        snapshots
        # Truncate to month and add to select list
        .annotate(month=TruncMonth("created_at"))
        # Group By month
        .values("month")
        # Select the avg/sum of the grouping
        .annotate(snapshots_count=Count("created_at", distinct=True))
        .annotate(locales_count=Count("project_locale__locale", distinct=True))
        .annotate(completion_avg=Avg("completion"))
        .annotate(human_translations_sum=Sum("human_translations"))
        .annotate(machinery_sum=Sum("machinery_translations"))
        .annotate(new_source_strings_sum=Sum("new_source_strings"))
        .annotate(unreviewed_sum=Sum("unreviewed_strings"))
        .annotate(peer_approved_sum=Sum("peer_approved"))
        .annotate(self_approved_sum=Sum("self_approved"))
        .annotate(rejected_sum=Sum("rejected"))
        .annotate(new_suggestions_sum=Sum("new_suggestions"))
        # Select month and values
        .values(
            "month",
            "snapshots_count",
            "locales_count",
            "completion_avg",
            "human_translations_sum",
            "machinery_sum",
            "new_source_strings_sum",
            "unreviewed_sum",
            "peer_approved_sum",
            "self_approved_sum",
            "rejected_sum",
            "new_suggestions_sum",
        )
        .order_by("month")
    )

    return {
        "dates": [convert_to_unix_time(x["month"]) for x in insights],
        "translation_activity": {
            "completion": [round(x["completion_avg"], 2) for x in insights],
            "human_translations": [x["human_translations_sum"] for x in insights],
            "machinery_translations": [x["machinery_sum"] for x in insights],
            # The same new source strings are added to each locale, so they need to be normalised
            "new_source_strings": [
                int(
                    round(
                        x["new_source_strings_sum"]
                        / (x["locales_count"] if x["locales_count"] != 0 else 1)
                    )
                )
                for x in insights
            ],
        },
        "review_activity": {
            # Unreviewed is not a delta, so use an average for the whole month
            "unreviewed": [
                int(
                    round(
                        x["unreviewed_sum"]
                        / (x["snapshots_count"] if x["snapshots_count"] != 0 else 1)
                    )
                )
                for x in insights
            ],
            "peer_approved": [x["peer_approved_sum"] for x in insights],
            "self_approved": [x["self_approved_sum"] for x in insights],
            "rejected": [x["rejected_sum"] for x in insights],
            "new_suggestions": [x["new_suggestions_sum"] for x in insights],
        },
    }
