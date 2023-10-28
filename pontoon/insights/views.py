import logging

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.utils import timezone

from pontoon.insights.utils import get_global_pretranslation_quality

log = logging.getLogger(__name__)


def insights(request):
    """Insights page."""
    if not settings.ENABLE_INSIGHTS:
        raise ImproperlyConfigured("ENABLE_INSIGHTS variable not set in settings.")

    return render(
        request,
        "insights/insights.html",
        {
            "start_date": timezone.now() - relativedelta(years=1),
            "end_date": timezone.now(),
            "team_pretranslation_quality": get_global_pretranslation_quality(
                "locale", "code"
            ),
            "project_pretranslation_quality": get_global_pretranslation_quality(
                "entity__resource__project", "slug"
            ),
        },
    )
