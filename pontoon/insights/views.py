import logging

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.utils import timezone

from pontoon.insights.utils import get_global_pretranslation_quality

log = logging.getLogger(__name__)


def insights(request):
    """Insights page."""
    if not settings.ENABLE_INSIGHTS:
        raise ImproperlyConfigured("ENABLE_INSIGHTS variable not set in settings.")

    team_pretranslation_quality = cache.get_or_set(
        f"/{__name__}/team_pretranslation_quality",
        get_global_pretranslation_quality("locale", "code"),
        settings.VIEW_CACHE_TIMEOUT,
    )

    project_pretranslation_quality = cache.get_or_set(
        f"/{__name__}/project_pretranslation_quality",
        get_global_pretranslation_quality("entity__resource__project", "slug"),
        settings.VIEW_CACHE_TIMEOUT,
    )

    return render(
        request,
        "insights/insights.html",
        {
            "start_date": timezone.now() - relativedelta(years=1),
            "end_date": timezone.now(),
            "team_pretranslation_quality": team_pretranslation_quality,
            "project_pretranslation_quality": project_pretranslation_quality,
        },
    )
