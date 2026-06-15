from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils import timezone

from pontoon.base.aggregated_stats import get_top_instances
from pontoon.base.forms import UserCommunityHealthDashboardConfigForm
from pontoon.base.models.locale import Locale
from pontoon.base.models.translated_resource import TranslatedResource
from pontoon.insights.chs import KEY_PROJECT_SLUGS
from pontoon.insights.models import LocaleHealthSnapshot
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
from pontoon.teams.forms import LocaleRequestForm


LOCALES = [
    # Top 15 (+es-CL)
    "cs",
    "de",
    "es-AR",
    "es-CL",
    "es-ES",
    "es-MX",
    "fr",
    "hu",
    "id",
    "it",
    "ja",
    "nl",
    "pl",
    "pt-BR",
    "ru",
    "zh-CN",
    # Top 25
    "tr",
    "el",
    "zh-TW",
    "fi",
    "pt-PT",
    "sv-SE",
    "vi",
    "sk",
    "ar",
    # Romanian
    "ro",
]

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


def get_monthly_snapshots(locales, month):
    month_start = month.replace(day=1)
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


@login_required(redirect_field_name="", login_url="/403")
def dashboard_config(request):
    """Configure which locales appear on the CHS dashboard."""
    user = request.user
    profile = user.profile

    if not user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        dashboard_locales_form = UserCommunityHealthDashboardConfigForm(
            request.POST, instance=profile
        )

        if dashboard_locales_form.is_valid():
            dashboard_locales_form.save()
            messages.success(request, "Configuration saved.")
            return redirect("pontoon.dashboard")

    dashboard_locales = profile.dashboard_locales

    locales = Locale.objects.visible()
    selected_locales = locales.filter(pk__in=dashboard_locales)
    available_locales = locales.exclude(pk__in=dashboard_locales)
    return render(
        request,
        "dashboard/config.html",
        {
            "available_locales": available_locales,
            "selected_locales": selected_locales,
        },
    )


@login_required(redirect_field_name="", login_url="/403")
def dashboard(request):
    """List all localization team CHS scores."""

    user = request.user
    profile = user.profile

    if not user.is_staff:
        raise PermissionDenied

    # TODO Include "Last Updated -> Next scheduled update timer" so PMs don't get confused
    # TODO Maybe also include a "Run failed" warning or the option to manually run CHS calculation
    dashboard_locales = profile.dashboard_locales
    locales = Locale.objects.visible().filter(pk__in=dashboard_locales).order_by("code")

    # TEMP: the most recent snapshot is from May, so shift the window back one
    # month — render the previous month as "current" and the month before as
    # "previous". Revert `current_anchor` to `timezone.now().date()` once the
    # current month has snapshots.
    current_anchor = timezone.now().date().replace(day=1) - relativedelta(days=1)
    previous_anchor = current_anchor.replace(day=1) - relativedelta(days=1)
    current_snapshots = get_monthly_snapshots(locales, current_anchor)
    previous_snapshots = get_monthly_snapshots(locales, previous_anchor)
    snapshot_base_deltas = get_monthly_snapshot_deltas(
        current_snapshots, previous_snapshots, CHS_BASE_METRICS
    )
    snapshot_score_deltas = get_monthly_snapshot_deltas(
        current_snapshots, previous_snapshots, CHS_SCORE_METRICS
    )

    form = LocaleRequestForm()

    locale_stats = locales.stats_data_as_dict()
    print(snapshot_base_deltas)
    print(snapshot_score_deltas)
    return render(
        request,
        "dashboard/dashboard.html",
        {
            "locales": locales,
            "current_snapshots": current_snapshots,
            "snapshot_base_deltas": snapshot_base_deltas,
            "snapshot_score_deltas": snapshot_score_deltas,
            "columns": CHS_COLUMNS,
            "all_locales_stats": TranslatedResource.objects.string_stats(),
            "locale_stats": locale_stats,
            "form": form,
            "top_instances": get_top_instances(locales, locale_stats),
        },
    )
