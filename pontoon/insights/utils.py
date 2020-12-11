from django.db.models.functions import TruncMonth
from django.db.models import Avg, Sum

from pontoon.base.utils import aware_datetime, convert_to_unix_time, get_last_months
from pontoon.insights.models import LocaleInsightsSnapshot


def get_insights(query_filters=None):
    """Get data required by the Insights tab.

    :param django.db.models.Q query_filters: filters insights by given query_filters.
    """
    months = sorted(
        [aware_datetime(year, month, 1) for year, month in get_last_months(12)]
    )

    snapshots = LocaleInsightsSnapshot.objects.filter(created_at__gte=months[0])

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

    latest = snapshots.latest("created_at") if snapshots else None
    active_users = latest.active_users_last_12_months if latest else None

    return {
        "dates": [convert_to_unix_time(month) for month in months],
        # Active users
        "total_managers": latest.total_managers if latest else 0,
        "total_reviewers": latest.total_reviewers if latest else 0,
        "total_contributors": latest.total_contributors if latest else 0,
        "active_managers": active_users["managers"] if active_users else 0,
        "active_reviewers": active_users["reviewers"] if active_users else 0,
        "active_contributors": active_users["contributors"] if active_users else 0,
        # Unreviewed suggestions lifespan
        "unreviewed_lifespans": [x["unreviewed_lifespan_avg"].days for x in insights],
        # Translation activity
        "translation_activity": {
            "completion": [round(x["completion_avg"], 2) for x in insights],
            "human_translations": [x["human_translations_sum"] for x in insights],
            "machinery_translations": [x["machinery_sum"] for x in insights],
            "new_source_strings": [x["new_source_strings_sum"] for x in insights],
        },
        # Review activity
        "review_activity": {
            "unreviewed": [int(round(x["unreviewed_avg"])) for x in insights],
            "peer_approved": [x["peer_approved_sum"] for x in insights],
            "self_approved": [x["self_approved_sum"] for x in insights],
            "rejected": [x["rejected_sum"] for x in insights],
            "new_suggestions": [x["new_suggestions_sum"] for x in insights],
        },
    }
