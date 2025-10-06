import logging

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import groupby
from statistics import mean
from typing import Any, Iterable, Iterator

from celery import shared_task
from dateutil.relativedelta import relativedelta
from sacrebleu.metrics import CHRF

from django.contrib.auth.models import User
from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import Extract, Now
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Entity, Locale, TranslatedResource, Translation
from pontoon.insights.models import (
    LocaleInsightsSnapshot,
    ProjectLocaleInsightsSnapshot,
)


chrfpp = CHRF(word_order=2)
log = logging.getLogger(__name__)


@dataclass
class Activity:
    locale: int
    human_translations: set[int] = field(default_factory=set)
    machinery_translations: set[int] = field(default_factory=set)
    new_suggestions: set[int] = field(default_factory=set)
    peer_approved: set[int] = field(default_factory=set)
    self_approved: set[int] = field(default_factory=set)
    rejected: set[int] = field(default_factory=set)
    pretranslations_chrf_scores: list[float] = field(default_factory=list)
    pretranslations_approved: set[int] = field(default_factory=set)
    pretranslations_rejected: set[int] = field(default_factory=set)
    pretranslations_new: set[int] = field(default_factory=set)
    times_to_review_suggestions: list[timedelta] = field(default_factory=list)
    times_to_review_pretranslations: list[timedelta] = field(default_factory=list)


@shared_task(bind=True)
def collect_insights(self, dt_max: datetime | None = None):
    """
    Gather data needed for the Insights tab and store it in the DB.
    """
    if dt_max is None:
        dt_max = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    date = dt_max.date()

    log.info(f"Collect insights for {date}: Begin.")

    activities = count_activities(dt_max)
    new_entities = count_created_entities(dt_max)
    pl_stats = count_projectlocale_stats()
    log.info(f"Collect insights for {date}: Common data gathered.")

    created = ProjectLocaleInsightsSnapshot.objects.bulk_create(
        projectlocale_insights(dt_max, activities, new_entities, pl_stats),
        batch_size=1000,
    )
    log.info(
        f"Collect insights for {date}: {len(created)} ProjectLocale insights created."
    )

    created = LocaleInsightsSnapshot.objects.bulk_create(
        locale_insights(dt_max, activities, new_entities, pl_stats),
        batch_size=1000,
    )
    log.info(f"Collect insights for {date}: {len(created)} Locale insights created.")


def count_activities(dt_max: datetime):
    """
    `projectlocale_id -> Activity`

    Fetch and prepare activity data.

    Note that this function is also called from
    pontoon.insights.migrations.0017_fix_projectlocale_insights_again and
    pontoon.insights.migrations.0018_fix_locale_insights,
    which may need a local copy if the behaviour here is modified.
    """
    res: dict[int, Activity] = dict()

    sync_user = User.objects.get(email="pontoon-sync@example.com").pk
    pretranslation_users: set[int] = set(
        User.objects.filter(
            email__in=["pontoon-tm@example.com", "pontoon-gt@example.com"]
        ).values_list("pk", flat=True)
    )

    actions = query_actions(dt_max)
    approved_translations = get_approved_translations(actions, pretranslation_users)

    for action in actions:
        key = action["projectlocale"]
        if key not in res:
            res[key] = Activity(locale=action["translation__locale"])
        data = res[key]

        approved_date: datetime | None = action["approved_date"]
        date: datetime = action["date"]
        performed_by: int = action["performed_by"]
        translation: int = action["translation"]
        user: int = action["user"]

        # Review actions performed by the sync process are ignored, because they
        # aren't explicit user review actions.
        performed_by_sync = performed_by == sync_user

        match action["action_type"]:
            case "translation:created":
                if not action["machinery_sources"]:
                    data.human_translations.add(translation)
                else:
                    data.machinery_translations.add(translation)
                if not approved_date or approved_date > date:
                    data.new_suggestions.add(translation)
                if user in pretranslation_users:
                    data.pretranslations_new.add(translation)
                # Self-approval can also happen on translation submission
                if performed_by == action["approved_user"] and not performed_by_sync:
                    data.self_approved.add(translation)

            case "translation:approved" if not performed_by_sync:
                if performed_by == user:
                    data.self_approved.add(translation)
                else:
                    data.peer_approved.add(translation)
                    if approved_date:
                        review_time = approved_date - date
                        data.times_to_review_suggestions.append(review_time)
                        if user in pretranslation_users:
                            data.times_to_review_pretranslations.append(review_time)
                if user in pretranslation_users:
                    data.pretranslations_approved.add(translation)
                    # Translation has been approved, no need to claculate the chrF++ score.
                    # Note that the score is assigned to the pretranslation review date
                    # rather than its creation date, which would be preferable.
                    data.pretranslations_chrf_scores.append(100)

            case "translation:rejected" if not performed_by_sync:
                data.rejected.add(translation)
                if action["rejected_date"]:
                    review_time = action["rejected_date"] - date
                    data.times_to_review_suggestions.append(review_time)
                    if user in pretranslation_users:
                        data.times_to_review_pretranslations.append(review_time)
                if user in pretranslation_users:
                    data.pretranslations_rejected.add(translation)
                    score = get_chrf_score(action, approved_translations)
                    if score:
                        data.pretranslations_chrf_scores.append(score)

    return res


def query_actions(dt_max: datetime):
    """Get actions of the previous day, needed to render charts."""
    return (
        ActionLog.objects.filter(
            created_at__gte=dt_max - relativedelta(days=1),
            created_at__lt=dt_max,
            translation__entity__resource__project__system_project=False,
            translation__entity__resource__project__visibility="public",
            translation__entity__resource__project__project_locale__locale=F(
                "translation__locale"
            ),
        )
        .values(
            "action_type",
            "performed_by",
            "translation",
            "translation__entity",
            "translation__locale",
            "translation__string",
            machinery_sources=F("translation__machinery_sources"),
            user=F("translation__user"),
            approved_user=F("translation__approved_user"),
            date=F("translation__date"),
            approved_date=F("translation__approved_date"),
            rejected_date=F("translation__rejected_date"),
            project=F("translation__entity__resource__project"),
            projectlocale=F("translation__entity__resource__project__project_locale"),
        )
        .order_by("translation__locale")
    )


def get_approved_translations(
    actions: Iterable[dict[str, Any]], pretranslation_users: set[int]
) -> dict[tuple[int, int], str]:
    """Fetch approved translations of entities with rejected pretranslations, needed for
    faster chrf++ score calculation."""
    rejected_pretranslation_actions = [
        action
        for action in actions
        if action["action_type"] == "translation:rejected"
        and action["user"] in pretranslation_users
    ]

    # This will catch a superset of required approved translations, which is much more
    # convenient to capture than the exact set, but doesn't seem to impact performance.
    approved_translations = Translation.objects.filter(
        entity__in={a["translation__entity"] for a in rejected_pretranslation_actions},
        locale__in={a["translation__locale"] for a in rejected_pretranslation_actions},
        approved=True,
    ).values("entity", "locale", "string")
    return {(t["entity"], t["locale"]): t["string"] for t in approved_translations}


def get_chrf_score(
    action: dict[str, Any], approved_translations: dict[tuple[int, int], str]
):
    approved_translation = approved_translations.get(
        (action["translation__entity"], action["translation__locale"]), None
    )
    if approved_translation is None:
        return None
    score = chrfpp.sentence_score(action["translation__string"], [approved_translation])
    return float(score.format(score_only=True))


def count_created_entities(dt_max: datetime) -> dict[int, tuple[int, int]]:
    """
    `projectlocale_id -> (locale_id, count)`

    Count entities created on the previous day for each projectlocale.

    Note that this function is also called from
    pontoon.insights.migrations.0018_fix_locale_insights,
    which may need a local copy if the behaviour here is modified.
    """
    return {
        d["projectlocale"]: (d["locale"], d["count"])
        for d in (
            Entity.objects.filter(
                date_created__gte=dt_max - relativedelta(days=1),
                date_created__lt=dt_max,
                obsolete=False,
                resource__project__disabled=False,
                resource__project__system_project=False,
                resource__project__visibility="public",
                resource__translatedresources__locale__project_locale__project=F(
                    "resource__project"
                ),
            )
            .distinct()
            .values(
                projectlocale=F(
                    "resource__translatedresources__locale__project_locale"
                ),
                locale=F(
                    "resource__translatedresources__locale__project_locale__locale"
                ),
            )
            .annotate(count=Count("*"))
        )
    }


def count_projectlocale_stats() -> Iterable[dict[str, int]]:
    """
    Note that this function is also called from
    pontoon.insights.migrations.0018_fix_locale_insights,
    which may need a local copy if the behaviour here is modified.
    """
    return (
        TranslatedResource.objects.filter(
            resource__project__disabled=False,
            resource__project__system_project=False,
            resource__project__visibility="public",
        )
        .filter(resource__project__project_locale__locale=F("locale"))
        .values("locale", projectlocale=F("resource__project__project_locale"))
        .annotate(
            total=Sum("total_strings", default=0),
            approved=Sum("approved_strings", default=0),
            pretranslated=Sum("pretranslated_strings", default=0),
            errors=Sum("strings_with_errors", default=0),
            warnings=Sum("strings_with_warnings", default=0),
            unreviewed=Sum("unreviewed_strings", default=0),
        )
        .order_by("locale")
    )


def projectlocale_insights(
    dt_max: datetime,
    activities: dict[int, Activity],
    new_entities: dict[int, tuple[int, int]],
    pl_stats: Iterable[dict[str, int]],
) -> Iterator[ProjectLocaleInsightsSnapshot]:
    for pls in pl_stats:
        id = pls["projectlocale"]
        ad = activities.get(id, Activity(0))
        pl_completion = (
            (pls["approved"] + pls["pretranslated"] + pls["warnings"]) / pls["total"]
            if pls["total"] > 0
            else 0.0
        )
        yield ProjectLocaleInsightsSnapshot(
            project_locale_id=pls["projectlocale"],
            created_at=dt_max,
            # Aggregateds stats
            total_strings=pls["total"],
            approved_strings=pls["approved"],
            pretranslated_strings=pls["pretranslated"],
            strings_with_errors=pls["errors"],
            strings_with_warnings=pls["warnings"],
            unreviewed_strings=pls["unreviewed"],
            # Translation activity
            completion=round(100 * pl_completion, 2),
            human_translations=len(ad.human_translations),
            machinery_translations=len(ad.machinery_translations),
            new_source_strings=new_entities.get(id, (0, 0))[1],
            # Review activity
            peer_approved=len(ad.peer_approved),
            self_approved=len(ad.self_approved),
            rejected=len(ad.rejected),
            new_suggestions=len(ad.new_suggestions),
            # Pretranslation quality
            pretranslations_chrf_score=(
                mean(ad.pretranslations_chrf_scores)
                if ad.pretranslations_chrf_scores
                else 0.0
            ),
            pretranslations_approved=len(ad.pretranslations_approved),
            pretranslations_rejected=len(ad.pretranslations_rejected),
            pretranslations_new=len(ad.pretranslations_new),
        )


def locale_insights(
    dt_max: datetime,
    activities: dict[int, Activity],
    new_entities: dict[int, tuple[int, int]],
    pl_stats: Iterable[dict[str, int]],
) -> Iterator[LocaleInsightsSnapshot]:
    """
    Note that this function is also called from
    pontoon.insights.migrations.0018_fix_locale_insights,
    which may need a local copy if the behaviour here is modified.
    """
    privileged_users = get_privileged_users()
    contributors = get_contributors()
    active_users_actions = get_active_users_actions(dt_max)
    suggestion_ages = get_average_suggestion_ages()
    for locale, lc_stats_iter in groupby(pl_stats, lambda ps: ps["locale"]):
        lc_activities = [a for a in activities.values() if a.locale == locale]
        lc_new_entities = sum(c for li, c in new_entities.values() if li == locale)
        lc_manager_logins, lc_translators = privileged_users[locale]
        yield (
            get_locale_insights_snapshot(
                locale,
                dt_max,
                lc_activities,
                lc_new_entities,
                lc_stats_iter,
                lc_manager_logins,
                lc_translators,
                contributors.get(locale, set()),
                active_users_actions.get(locale, []),
                suggestion_ages.get(locale, timedelta()),
            )
        )


def get_privileged_users() -> dict[int, tuple[dict[int, datetime], set[int]]]:
    """
    `locale_id -> ({manager_id: manager_last_login}, {translator_id})`
    """
    data: Iterator[dict[str, Any]] = (
        Locale.objects.available()
        .values(
            locale=F("pk"),
            manager_login=F("managers_group__user__last_login"),
            manager=F("managers_group__user"),
            translator=F("translators_group__user"),
        )
        .order_by("locale")
    )
    res: dict[int, tuple[dict[int, datetime], set[int]]] = {}
    for locale, group in groupby(data, lambda u: u["locale"]):
        manager_logins: dict[int, datetime] = {
            manager: row["manager_login"]
            for row in group
            if (manager := row["manager"])
        }
        translators: set[int] = {
            translator for row in group if (translator := row["translator"])
        }
        res[locale] = (manager_logins, translators)
    return res


def get_contributors() -> dict[int, set[int]]:
    """
    Get all contributors without system users.

    Note that excluding system user emails in the Translation QuerySet directly is slow.
    """
    contributors = (
        Translation.objects.filter(user__isnull=False)
        .exclude(user__in=User.objects.filter(profile__system_user=True))
        .values("locale", "user")
        .order_by("locale")
        .distinct()
    )
    return {
        locale: {g["user"] for g in group}
        for locale, group in groupby(contributors, lambda c: c["locale"])
    }


def get_active_users_actions(
    dt_max: datetime,
) -> dict[int, list[dict[str, Any]]]:
    """Get actions of the previous year, needed for the Active users charts."""
    actions = (
        ActionLog.objects.filter(
            created_at__gte=dt_max - relativedelta(year=1),
            created_at__lt=dt_max,
        )
        .values("action_type", "created_at", "performed_by", "translation__locale")
        .order_by("translation__locale")
        .distinct()
    )
    return {
        locale: list(group)
        for locale, group in groupby(actions, lambda a: a["translation__locale"])
    }


def get_average_suggestion_ages() -> dict[int, timedelta]:
    """Get currently unreviewed suggestions for each locale."""
    suggestions = (
        Translation.objects.filter(
            # Make sure TranslatedResource is still enabled for the locale
            locale=F("entity__resource__translatedresources__locale"),
            approved=False,
            pretranslated=False,
            fuzzy=False,
            rejected=False,
            entity__obsolete=False,
            entity__resource__project__disabled=False,
            entity__resource__project__system_project=False,
            entity__resource__project__visibility="public",
        )
        .values("locale")
        .annotate(avg_age=Avg(Extract(Now(), "epoch") - Extract(F("date"), "epoch")))
    )
    return {s["locale"]: timedelta(s["avg_age"]) for s in suggestions}


def get_locale_insights_snapshot(
    locale: int,
    dt_max: datetime,
    activities: list[Activity],
    entities_count,
    stats_iter: Iterator[dict[str, int]],
    manager_logins: dict[int, datetime],
    translators: set[int],
    contributors: set[int],
    active_users_actions: list[dict[str, Any]],
    avg_suggestion_age: timedelta,
):
    """Create LocaleInsightsSnapshot instance for the given locale and day using given data."""
    avg_suggestion_review_age, avg_pt_review_age = get_review_ages(activities)
    ma = merge_activities(activities)
    pt_chrf_score = (
        mean(ma.pretranslations_chrf_scores) if ma.pretranslations_chrf_scores else 0
    )

    ls_total = 0
    ls_approved = 0
    ls_pretranslated = 0
    ls_errors = 0
    ls_warnings = 0
    ls_unreviewed = 0
    for ls in stats_iter:
        ls_total += ls["total"]
        ls_approved += ls["approved"]
        ls_pretranslated += ls["pretranslated"]
        ls_errors += ls["errors"]
        ls_warnings += ls["warnings"]
        ls_unreviewed += ls["unreviewed"]
    ls_completion = (
        (ls_approved + ls_pretranslated + ls_warnings) / ls_total
        if ls_total > 0
        else 0.0
    )

    reviewers = translators | manager_logins.keys()
    active_users = {
        months: get_active_users(
            dt_max - relativedelta(months=months),
            manager_logins,
            active_users_actions,
            reviewers,
            contributors,
        )
        for months in [1, 3, 6, 12]
    }

    return LocaleInsightsSnapshot(
        locale_id=locale,
        created_at=dt_max,
        # Aggregated stats
        total_strings=ls_total,
        approved_strings=ls_approved,
        pretranslated_strings=ls_pretranslated,
        strings_with_errors=ls_errors,
        strings_with_warnings=ls_warnings,
        unreviewed_strings=ls_unreviewed,
        # Active users
        total_managers=len(manager_logins),
        total_reviewers=len(reviewers),
        total_contributors=len(contributors),
        active_users_last_month=active_users[1],
        active_users_last_3_months=active_users[3],
        active_users_last_6_months=active_users[6],
        active_users_last_12_months=active_users[12],
        unreviewed_suggestions_lifespan=avg_suggestion_age,
        time_to_review_suggestions=avg_suggestion_review_age,
        time_to_review_pretranslations=avg_pt_review_age,
        # Translation activity
        completion=round(100 * ls_completion, 2),
        human_translations=len(ma.human_translations),
        machinery_translations=len(ma.machinery_translations),
        new_source_strings=entities_count,
        # Review activity
        peer_approved=len(ma.peer_approved),
        self_approved=len(ma.self_approved),
        rejected=len(ma.rejected),
        new_suggestions=len(ma.new_suggestions),
        # Pretranslation quality
        pretranslations_chrf_score=pt_chrf_score,
        pretranslations_approved=len(ma.pretranslations_approved),
        pretranslations_rejected=len(ma.pretranslations_rejected),
        pretranslations_new=len(ma.pretranslations_new),
    )


def get_review_ages(activities: list[Activity]):
    """Get average times to review suggestions and pretranslations."""
    sum_suggestions = timedelta()
    count_suggestions = 0
    sum_pretranslations = timedelta()
    count_pretranslations = 0
    for data in activities:
        sum_suggestions = sum(data.times_to_review_suggestions, sum_suggestions)
        count_suggestions += len(data.times_to_review_suggestions)
        sum_pretranslations = sum(
            data.times_to_review_pretranslations, sum_pretranslations
        )
        count_pretranslations += len(data.times_to_review_pretranslations)

    avg_suggestion_time = (
        sum_suggestions / count_suggestions if count_suggestions else None
    )
    avg_pretranslation_time = (
        sum_pretranslations / count_pretranslations if count_pretranslations else None
    )
    return avg_suggestion_time, avg_pretranslation_time


def merge_activities(activities: list[Activity]) -> Activity:
    """Get data for Translation activity and Review activity charts."""
    res = Activity(0)
    for data in activities:
        res.human_translations.update(data.human_translations)
        res.machinery_translations.update(data.machinery_translations)
        res.new_suggestions.update(data.new_suggestions)
        res.peer_approved.update(data.peer_approved)
        res.self_approved.update(data.self_approved)
        res.rejected.update(data.rejected)
        res.pretranslations_chrf_scores.extend(data.pretranslations_chrf_scores)
        res.pretranslations_approved.update(data.pretranslations_approved)
        res.pretranslations_rejected.update(data.pretranslations_rejected)
        res.pretranslations_new.update(data.pretranslations_new)
    return res


def get_active_users(
    start_time: datetime,
    manager_logins: dict[int, datetime],
    actions: list[dict[str, Any]],
    locale_reviewers: set[int],
    locale_contributors: set[int],
):
    active_reviewers = set()
    active_contributors = set()
    for action in actions:
        if action["created_at"] > start_time:
            action_user: int = action["performed_by"]
            match action["action_type"]:
                case "translation:created":
                    active_contributors.add(action_user)
                case (
                    "translation:approved"
                    | "translation:unapproved"
                    | "translation:rejected"
                    | "translation:unrejected"
                ):
                    active_reviewers.add(action_user)

    # Filter active reviewers and contributors;
    # otherwise we might include PMs and privileged users of other locales.
    return {
        "managers": sum(1 for t in manager_logins.values() if t > start_time),
        "reviewers": len(active_reviewers & locale_reviewers),
        "contributors": len(active_contributors & locale_contributors),
    }
