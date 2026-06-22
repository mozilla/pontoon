import logging

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.utils import timezone

from pontoon.base.models.locale import Locale
from pontoon.insights.utils import (
    get_global_locale_health_insights,
    get_global_pretranslation_quality,
)


log = logging.getLogger(__name__)


def insights(request):
    """Insights page."""
    if not settings.ENABLE_INSIGHTS:
        raise ImproperlyConfigured("ENABLE_INSIGHTS variable not set in settings.")

    # Cannot use cache.get_or_set(), because it always calls the slow function
    # get_global_pretranslation_quality(). The reason we use cache in first place is to
    # avoid that.

    team_pt_key = f"/{__name__}/team_pretranslation_quality"
    team_pretranslation_quality = cache.get(team_pt_key)
    if not team_pretranslation_quality:
        team_pretranslation_quality = get_global_pretranslation_quality(
            "locale", "code"
        )
        cache.set(team_pt_key, team_pretranslation_quality, settings.VIEW_CACHE_TIMEOUT)

    project_pt_key = f"/{__name__}/project_pretranslation_quality"
    project_pretranslation_quality = cache.get(project_pt_key)
    if not project_pretranslation_quality:
        project_pretranslation_quality = get_global_pretranslation_quality(
            "entity__resource__project", "slug"
        )
        cache.set(
            project_pt_key, project_pretranslation_quality, settings.VIEW_CACHE_TIMEOUT
        )

    global_locale_health_insights = []
    user = request.user
    if user.is_staff:
        locale_ids = user.profile.dashboard_locales
        locales = Locale.objects.filter(pk__in=locale_ids)
        global_locale_health_insights = get_global_locale_health_insights(locales)

    return render(
        request,
        "insights/insights.html",
        {
            "start_date": timezone.now() - relativedelta(years=1),
            "end_date": timezone.now(),
            "team_pretranslation_quality": team_pretranslation_quality,
            "project_pretranslation_quality": project_pretranslation_quality,
            "global_locale_health_insights": global_locale_health_insights,
        },
    )
