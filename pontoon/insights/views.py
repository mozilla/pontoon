import logging

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from pontoon.base.models.locale import Locale
from pontoon.base.utils import require_AJAX
from pontoon.insights.chs import KEY_PROJECT_SLUGS
from pontoon.insights.forms import CommunityHealthLocalesForm
from pontoon.insights.models import LocaleHealthSnapshot
from pontoon.insights.utils import (
    get_global_locale_health_insights,
    get_global_pretranslation_quality,
)
from pontoon.settings.base import (
    ACTIVE_CONTRIBUTOR_PEOPLE_THRESHOLD,
    ACTIVE_CONTRIBUTOR_POINTS,
    ALL_CONTRIBUTOR_PEOPLE_THRESHOLD,
    ALL_CONTRIBUTOR_POINTS,
    COMPLETION_POINTS,
    ENABLED_PROJECT_POINTS,
    MANAGER_PEOPLE_THRESHOLD,
    MANAGER_POINTS,
    NEW_SIGNUP_PEOPLE_THRESHOLD,
    NEW_SIGNUP_POINTS,
    TRANSLATOR_PEOPLE_THRESHOLD,
    TRANSLATOR_POINTS,
)


log = logging.getLogger(__name__)


CHS_BASE_METRICS = [
    "active_managers",
    "active_translators",
    "active_contributors",
    "all_contributors",
    "new_signups",
    "key_projects_enabled",
    "completion",
    "chs",
]

CHS_SCORE_METRICS = [
    "key_projects_enabled_score",
    "active_managers_score",
    "active_translators_score",
    "active_contributors_score",
    "all_contributors_score",
    "new_signups_score",
    "completion_score",
    "chs",
]

CHS_COLUMNS = {
    "active_managers": {
        "base_threshold": MANAGER_PEOPLE_THRESHOLD,
        "score_threshold": MANAGER_POINTS,
    },
    "active_translators": {
        "base_threshold": TRANSLATOR_PEOPLE_THRESHOLD,
        "score_threshold": TRANSLATOR_POINTS,
    },
    "active_contributors": {
        "base_threshold": ACTIVE_CONTRIBUTOR_PEOPLE_THRESHOLD,
        "score_threshold": ACTIVE_CONTRIBUTOR_POINTS,
    },
    "all_contributors": {
        "base_threshold": ALL_CONTRIBUTOR_PEOPLE_THRESHOLD,
        "score_threshold": ALL_CONTRIBUTOR_POINTS,
    },
    "new_signups": {
        "base_threshold": NEW_SIGNUP_PEOPLE_THRESHOLD,
        "score_threshold": NEW_SIGNUP_POINTS,
    },
    "key_projects_enabled": {
        "base_threshold": len(KEY_PROJECT_SLUGS),
        "score_threshold": ENABLED_PROJECT_POINTS,
    },
    "completion": {
        "base_threshold": 100,
        "percent": True,
        "score_threshold": COMPLETION_POINTS,
    },
    "chs": {"base_threshold": 100},
}


def get_monthly_snapshots(locales, date):
    month_start = date.replace(day=1)
    next_month_start = month_start + relativedelta(months=1)

    snapshots = LocaleHealthSnapshot.objects.filter(
        locale__in=locales,
        created_at__gte=month_start,
        created_at__lt=next_month_start,
    ).order_by("locale_id", "-created_at")

    latest = {}
    for snapshot in snapshots:
        latest.setdefault(snapshot.locale_id, snapshot)

    return latest


def get_monthly_snapshot_deltas(current_snapshots, previous_snapshots, metrics):
    deltas = {}
    for locale_id, curr_snapshot in current_snapshots.items():
        prev_snapshot = previous_snapshots.get(locale_id)
        locale_deltas = {}
        for column_key in metrics:
            if prev_snapshot is None:
                locale_deltas[column_key] = None
                continue
            curr_value = getattr(curr_snapshot, column_key)
            prev_value = getattr(prev_snapshot, column_key)
            locale_deltas[column_key] = curr_value - prev_value
        deltas[locale_id] = locale_deltas

    return deltas


def _community_health_context(profile):
    community_health_locales = profile.community_health_locales
    locales = Locale.objects.visible()
    display_locales = locales.filter(pk__in=community_health_locales).order_by("code")

    current_anchor = timezone.now().date()
    previous_anchor = current_anchor.replace(day=1) - relativedelta(days=1)
    current_snapshots = get_monthly_snapshots(display_locales, current_anchor)
    previous_snapshots = get_monthly_snapshots(display_locales, previous_anchor)

    return {
        "display_locales": display_locales,
        "current_snapshots": current_snapshots,
        "snapshot_base_deltas": get_monthly_snapshot_deltas(
            current_snapshots, previous_snapshots, CHS_BASE_METRICS
        ),
        "snapshot_score_deltas": get_monthly_snapshot_deltas(
            current_snapshots, previous_snapshots, CHS_SCORE_METRICS
        ),
        "columns": CHS_COLUMNS,
        "global_locale_health_insights": get_global_locale_health_insights(
            display_locales
        ),
    }


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@transaction.atomic
@require_AJAX
def edit_locales(request):

    if not settings.ENABLE_INSIGHTS:
        raise ImproperlyConfigured("ENABLE_INSIGHTS variable not set in settings.")

    user = request.user
    profile = user.profile

    if not user.is_staff:
        raise PermissionDenied

    community_health_locales_form = CommunityHealthLocalesForm(
        request.POST, instance=profile
    )

    if community_health_locales_form.is_valid():
        community_health_locales_form.save()

    else:
        return JsonResponse(
            {
                "status": "error",
                "message": "Form validation failed.",
                "errors": community_health_locales_form.errors,
            },
            status=400,
        )

    return JsonResponse({"status": True})


@login_required(redirect_field_name="", login_url="/403")
@require_AJAX
def render_panel(request):

    if not settings.ENABLE_INSIGHTS:
        raise ImproperlyConfigured("ENABLE_INSIGHTS variable not set in settings.")

    user = request.user
    profile = user.profile

    if not user.is_staff:
        raise PermissionDenied

    html = render_to_string(
        "insights/widgets/community_health_table_template.html",
        _community_health_context(profile),
        request,
    )

    return JsonResponse({"status": True, "html": html})


@login_required(redirect_field_name="", login_url="/403")
def insights(request):
    """Insights page."""

    if not settings.ENABLE_INSIGHTS:
        raise ImproperlyConfigured("ENABLE_INSIGHTS variable not set in settings.")

    user = request.user
    profile = user.profile

    if not user.is_staff:
        raise PermissionDenied

    community_health_locales = profile.community_health_locales
    locales = Locale.objects.visible()
    selected_locales = locales.filter(pk__in=community_health_locales)
    available_locales = locales.exclude(pk__in=community_health_locales)

    community_health_context = _community_health_context(profile)

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

    return render(
        request,
        "insights/insights.html",
        {
            "start_date": timezone.now() - relativedelta(years=1),
            "end_date": timezone.now(),
            "available_locales": available_locales,
            "selected_locales": selected_locales,
            "team_pretranslation_quality": team_pretranslation_quality,
            "project_pretranslation_quality": project_pretranslation_quality,
            **community_health_context,
        },
    )
