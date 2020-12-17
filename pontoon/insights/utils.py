from django.db.models.functions import TruncMonth
from django.db.models import Avg, Sum

from pontoon.base.utils import aware_datetime, convert_to_unix_time, get_last_months
from pontoon.insights.models import LocaleInsightsSnapshot, active_users_default


def get_insights(query_filters=None):
    """Get data required by the Insights tab.

    :param django.db.models.Q query_filters: filters insights by given query_filters.
    """
    months = sorted(
        [aware_datetime(year, month, 1) for year, month in get_last_months(12)]
    )

    return {
        "dates": [convert_to_unix_time(month) for month in months],
        # Active users
        "total": {
            "managers": 3,
            "reviewers": 7,
            "contributors": 29,
        },
        "active_users_last_month": {
            "managers": 1,
            "reviewers": 2,
            "contributors": 1,
        },
        "active_users_last_3_months": {
            "managers": 2,
            "reviewers": 3,
            "contributors": 3,
        },
        "active_users_last_6_months": {
            "managers": 2,
            "reviewers": 4,
            "contributors": 6,
        },
        "active_users_last_12_months": {
            "managers": 3,
            "reviewers": 5,
            "contributors": 12,
        },
        # Unreviewed suggestions lifespan
        "unreviewed_lifespans": [67, 73, 68, 71, 70, 69, 75, 68, 65, 67, 70, 67],
        # Translation activity
        "translation_activity": {
            "completion": [94.84, 94.69, 94.06, 94.98, 94.66, 92.93, 94.84, 95.6, 95.48, 95.29, 95.58, 95.1],
            "human_translations": [170, 160, 170, 180, 140, 190, 160, 100, 170, 170, 170, 100],
            "machinery_translations": [65, 90, 90, 60, 80, 65, 90, 60, 115, 65, 85, 25],
            "new_source_strings": [57, 39, 54, 39, 48, 45, 45, 51, 51, 45, 48, 27],
        },
        # Review activity
        "review_activity": {
            "unreviewed": [73, 77, 81, 71, 76, 73, 77, 74, 72, 74, 59, 72],
            "peer_approved": [100, 80, 45, 85, 75, 60, 80, 80, 75, 80, 85, 25],
            "self_approved": [155, 115, 140, 140, 150, 155, 200, 190, 165, 140, 125, 90],
            "rejected": [45, 42, 51, 48, 39, 63, 48, 57, 39, 48, 33, 15],
            "new_suggestions": [108, 96, 132, 104, 124, 116, 132, 140, 156, 124, 104, 76],
        },
    }
