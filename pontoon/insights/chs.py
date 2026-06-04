from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta

from django.db.models import Count, F, Q, Sum

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Locale, TranslatedResource, Translation
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.insights.models import LocaleChsSnapshot


KEY_PROJECT_SLUGS = [
    "firefox-for-android",
    "firefox-for-ios",
    "mozilla-monitor-website",
    "firefox-relay-website",
    "firefox",
    "mozilla-accounts",
    "mozilla-vpn-client",
]

# Contribution Data
MANAGER_STRING_THRESHOLD = 500
TRANSLATOR_STRING_THRESHOLD = 400
CONTRIBUTOR_THRESHOLD = 200
CONTRIBUTOR_APPROVED_THRESHOLD = 200
NEW_SIGNUP_SUBMISSION_THRESHOLD = 100

# CHS score calculation
MANAGER_PEOPLE_THRESHOLD = 1
TRANSLATOR_PEOPLE_THRESHOLD = 2
CONTRIBUTOR_PEOPLE_THRESHOLD = 2
CONTRIBUTOR_200_APPROVED_PEOPLE_THRESHOLD = 2
NEW_SIGNUP_PEOPLE_THRESHOLD = 2

MANAGER_POINTS = 20.0
TRANSLATOR_POINTS = 15.0
CONTRIBUTOR_POINTS = 4.0
CONTRIBUTOR_200_APPROVED_POINTS = 6.0
NEW_SIGNUP_POINTS = 5.0
ENABLED_PROJECT_POINTS = 4.0
COMPLETION_POINTS = 46.0


def get_completion_by_locale(locales) -> dict[int, float]:
    """Locale-level completion %: (approved + warnings) / total * 100."""

    locale_groupings = (
        TranslatedResource.objects.filter(
            locale__in=locales,
            resource__project__disabled=False,
            resource__project__system_project=False,
            resource__project__visibility="public",
        )
        .values("locale")
        .annotate(
            total=Sum("total_strings", default=0),
            approved=Sum("approved_strings", default=0),
            warnings=Sum("strings_with_warnings", default=0),
        )
    )

    locale_completion = {
        l_grouping["locale"]: round(
            100
            * (l_grouping["approved"] + l_grouping["warnings"])
            / l_grouping["total"],
            2,
        )
        if l_grouping["total"] > 0
        else 0.0
        for l_grouping in locale_groupings
    }

    return locale_completion


def get_key_projects_enabled_by_locale(
    locales, key_project_slugs: list[str]
) -> dict[int, int]:
    """Count of active key projects enabled for each locale."""
    pl_counts = (
        ProjectLocale.objects.filter(
            locale__in=locales,
            project__slug__in=key_project_slugs,
            project__disabled=False,
        )
        .values("locale_id")
        .annotate(count=Count("id"))
    )
    return {pl_count["locale_id"]: pl_count["count"] for pl_count in pl_counts}


def get_contributor_metrics_by_locale(locales, end_date: datetime) -> dict[int, dict]:
    """
    Per-locale active-contributor counts over the 12-month window ending at end_dt.
    """
    start_date = end_date - relativedelta(months=13)
    (print("start date", start_date),)
    print("end date", end_date)

    managers = defaultdict(set)
    translators = defaultdict(set)
    for row in locales.values(
        "pk",
        manager=F("managers_group__user"),
        translator=F("translators_group__user"),
    ):
        if row["manager"] is not None:
            managers[row["pk"]].add(row["manager"])
        if row["translator"] is not None:
            translators[row["pk"]].add(row["translator"])

    action_counts = {
        (row["performed_by"], row["locale_pk"]): row["action_count"]
        for row in (
            ActionLog.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                action_type__in=[
                    ActionLog.ActionType.TRANSLATION_APPROVED,
                    ActionLog.ActionType.TRANSLATION_REJECTED,
                ],
                translation__locale__in=locales,
                performed_by__profile__system_user=False,
            )
            .values("performed_by", locale_pk=F("translation__locale"))
            .annotate(action_count=Count("id"))
        )
    }

    contributor_translations = (
        Translation.objects.filter(
            locale__in=locales,
            user__isnull=False,
            user__profile__system_user=False,
            date__gte=start_date,
            date__lte=end_date,
        )
        .values(
            "locale_id",
            "user_id",
            joined=F("user__date_joined"),
            is_superuser=F("user__is_superuser"),
        )
        .annotate(
            total_count=Count("id"),
            approved_count=Count("id", filter=Q(approved=True)),
        )
    )

    locale_contributors = {
        locale.pk: {
            "active_managers": 0,
            "active_translators": 0,
            "active_contributors": 0,
            "active_contributors_200_approved": 0,
            "new_signups": 0,
        }
        for locale in locales
    }

    for row in contributor_translations:
        locale_id = row["locale_id"]
        user_id = row["user_id"]
        joined = row["joined"]
        is_superuser = row["is_superuser"]
        total = row["total_count"]
        approved = row["approved_count"]

        action_count = action_counts.get((user_id, locale_id), 0)

        if locale_id == 185:
            print("user_id", user_id)
            print("total", total)
            print("approved", approved)

        if not total:
            continue

        if user_id in managers[locale_id]:
            if action_count + approved > MANAGER_STRING_THRESHOLD:
                locale_contributors[locale_id]["active_managers"] += 1
        elif user_id in translators[locale_id]:
            if action_count + approved > TRANSLATOR_STRING_THRESHOLD:
                locale_contributors[locale_id]["active_translators"] += 1
        else:
            if is_superuser:
                continue
            if total > CONTRIBUTOR_THRESHOLD:
                locale_contributors[locale_id]["active_contributors"] += 1
            if approved > CONTRIBUTOR_APPROVED_THRESHOLD:
                locale_contributors[locale_id]["active_contributors_200_approved"] += 1
            if approved > NEW_SIGNUP_SUBMISSION_THRESHOLD and joined >= start_date:
                locale_contributors[locale_id]["new_signups"] += 1

    return locale_contributors


def compute_chs(args: dict) -> float:
    active_managers = args.get("active_managers", 0)
    active_translators = args.get("active_translators", 0)
    active_contributors = args.get("active_contributors", 0)
    active_contributors_200_approved = args.get("active_contributors_200_approved", 0)
    new_signups = args.get("new_signups", 0)
    key_projects_enabled = args.get("key_projects_enabled", 0)
    completion = args.get("completion", 0.0)

    total_manager_points = MANAGER_POINTS if active_managers >= 1 else 0

    if active_translators >= 2:
        total_translator_points = TRANSLATOR_POINTS
    elif active_translators >= 1:
        total_translator_points = TRANSLATOR_POINTS / 2
    else:
        total_translator_points = 0

    if active_contributors >= 2:
        total_contributor_points = CONTRIBUTOR_POINTS
    elif active_contributors >= 1:
        total_contributor_points = CONTRIBUTOR_POINTS / 2
    else:
        total_contributor_points = 0

    if active_contributors_200_approved >= 2:
        total_contributor_200_approved_points = CONTRIBUTOR_200_APPROVED_POINTS
    elif active_contributors_200_approved >= 1:
        total_contributor_200_approved_points = CONTRIBUTOR_200_APPROVED_POINTS / 2
    else:
        total_contributor_200_approved_points = 0

    if new_signups >= 2:
        total_new_signup_points = NEW_SIGNUP_POINTS
    elif new_signups >= 1:
        total_new_signup_points = NEW_SIGNUP_POINTS / 2
    else:
        total_new_signup_points = 0

    total_enabled_project_points = (
        key_projects_enabled / len(KEY_PROJECT_SLUGS)
    ) * ENABLED_PROJECT_POINTS
    total_completion_points = round((completion / 100) * COMPLETION_POINTS, 1)

    chs_score = (
        total_manager_points
        + total_translator_points
        + total_contributor_points
        + total_contributor_200_approved_points
        + total_new_signup_points
        + total_enabled_project_points
        + total_completion_points
    )

    return round(chs_score, 2)


def build_chs_snapshots(end_date: datetime) -> list[LocaleChsSnapshot]:
    """Assemble one LocaleChsSnapshot per available locale for dt_max."""
    locales = Locale.objects.visible()

    completion = get_completion_by_locale(locales)
    enabled = get_key_projects_enabled_by_locale(locales, KEY_PROJECT_SLUGS)
    contributors = get_contributor_metrics_by_locale(locales, end_date)

    snapshots = []
    for locale in locales:
        c = contributors.get(locale.pk, {})
        args = {
            "completion": completion.get(locale.pk, 0.0),
            "key_projects_enabled": enabled.get(locale.pk, 0),
            "active_managers": c.get("active_managers", 0),
            "active_translators": c.get("active_translators", 0),
            "active_contributors": c.get("active_contributors", 0),
            "active_contributors_200_approved": c.get(
                "active_contributors_200_approved", 0
            ),
            "new_signups": c.get("new_signups", 0),
        }
        chs_score = compute_chs(args)

        snapshots.append(
            LocaleChsSnapshot(
                locale=locale,
                created_at=end_date,
                **args,
                chs_score=chs_score,
            )
        )

    return snapshots
