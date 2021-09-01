from datetime import datetime
from django.db.models.functions import TruncMonth
from django.db.models import Avg, Sum

from pontoon.base.utils import convert_to_unix_time
from pontoon.insights.models import (
    LocaleInsightsSnapshot,
    ProjectInsightsSnapshot,
    active_users_default,
)


def get_insight_start_date(from2021=False):
    """Include at most the last year of data in insights.

    For project insights, data is only available from 2020-12-14 onwards,
    so limit queries to start from 2021-01-01 at earliest.
    """
    now = datetime.now()
    if from2021 and now.year == 2021:
        return datetime(2021, 1, 1)
    if now.month == 12:
        return datetime(now.year, 1, 1)
    return datetime(now.year - 1, now.month + 1, 1)


def get_locale_insights(query_filters=None):
    """Get data required by the Locale Insights tab.

    :param django.db.models.Q query_filters: filters insights by given query_filters.
    """
    start_date = get_insight_start_date(False)
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


def get_project_insights(query_filters=None):
    """Get data required by the Project Insights tab.

    :param django.db.models.Q query_filters: filters insights by given query_filters.
    """
    start_date = get_insight_start_date(True)
    snapshots = ProjectInsightsSnapshot.objects.filter(created_at__gte=start_date)

    if query_filters:
        snapshots = snapshots.filter(query_filters)

    insights = (
        snapshots
        # Truncate to month and add to select list
        .annotate(month=TruncMonth("created_at"))
        # Group By month
        .values("month")
        # Select the avg/sum of the grouping
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

    return {
        "dates": [convert_to_unix_time(x["month"]) for x in insights],
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
