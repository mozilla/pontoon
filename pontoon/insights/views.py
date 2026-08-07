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
from pontoon.insights.forms import CommunityHealthLocalesForm
from pontoon.insights.utils import (
    CHS_BASE_METRICS,
    CHS_SCORE_METRICS,
    get_chs_columns,
    get_global_locale_health_insights,
    get_global_pretranslation_quality,
    get_monthly_snapshot_deltas,
    get_monthly_snapshots,
)


log = logging.getLogger(__name__)


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
        "columns": get_chs_columns(),
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
