import logging

from celery import shared_task
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Count, F
from django.contrib.auth.models import User
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Entity, Locale, ProjectLocale, Translation
from pontoon.base.utils import group_dict_by
from pontoon.insights.models import (
    LocaleInsightsSnapshot,
    ProjectLocaleInsightsSnapshot,
)


log = logging.getLogger(__name__)


@shared_task(bind=True)
def collect_insights(self):
    """
    Gather data needed for the Insights tab and store it in the DB.
    """
    start_of_today = (
        timezone.now()
        .replace(hour=0)
        .replace(minute=0)
        .replace(second=0)
        .replace(microsecond=0)
    )

    date = start_of_today.date()

    log.info(f"Collect insights for {date}: Begin.")

    sync_user = User.objects.get(email="pontoon-sync@example.com").pk
    activities = build_activity_charts_data(start_of_today, sync_user)
    entities = query_entities(start_of_today)
    log.info(f"Collect insights for {date}: Common data gathered.")

    collect_project_locale_insights(start_of_today, activities, entities)
    log.info(f"Collect insights for {date}: ProjectLocale insights created.")

    collect_locale_insights(start_of_today, activities, entities)
    log.info(f"Collect insights for {date}: Locale insights created.")


def collect_project_locale_insights(start_of_today, activities, entities):
    """
    Collect insights for each available ProjectLocale.
    """
    ProjectLocaleInsightsSnapshot.objects.bulk_create(
        [
            get_project_locale_insights_snapshot(
                project_locale,
                start_of_today,
                activities,
                count_entities(
                    entities,
                    locale=project_locale.locale.id,
                    project=project_locale.project.id,
                ),
            )
            for project_locale in ProjectLocale.objects.all()
        ],
        batch_size=1000,
    )


def collect_locale_insights(start_of_today, activities, entities):
    """
    Collect insights for each available Locale.
    """
    # Get data sources to retrieve insights from
    privileged_users = get_privileged_users()
    contributors = get_contributors()
    active_users_actions = get_active_users_actions(start_of_today)
    suggestions = get_suggestions()

    LocaleInsightsSnapshot.objects.bulk_create(
        [
            get_locale_insights_snapshot(
                locale,
                start_of_today,
                privileged_users[locale.id],
                contributors[locale.id],
                active_users_actions[locale.id],
                suggestions[locale.id],
                activities,
                count_entities(entities, locale=locale.id),
            )
            for locale in Locale.objects.available()
        ],
        batch_size=1000,
    )


def get_privileged_users():
    """Get managers and translators."""
    privileged_users = (
        Locale.objects.available()
        .prefetch_related("managers_group__user_set", "translators_group__user_set")
        .values(
            "pk",
            "managers_group__user__last_login",
            "managers_group__user",
            "translators_group__user",
        )
    )

    return group_dict_by(privileged_users, "pk")


def get_contributors():
    """Get all contributors without system users.

    Note that excluding system user emails in the Translation QuerySet directly is slow.
    """
    system_users = User.objects.filter(profile__system_user=True).values("pk")

    contributors = (
        Translation.objects.filter(user__isnull=False)
        .exclude(user__pk__in=system_users)
        .values("locale", "user")
        .distinct()
    )

    return group_dict_by(contributors, "locale")


def get_active_users_actions(start_of_today):
    """Get actions of the previous year, needed for the Active users charts."""
    actions = (
        ActionLog.objects.filter(
            created_at__gte=start_of_today - relativedelta(year=1),
            created_at__lt=start_of_today,
        )
        .values("action_type", "created_at", "performed_by", "translation__locale")
        .distinct()
    )

    return group_dict_by(actions, "translation__locale")


def get_suggestions():
    """Get currently unreviewed suggestions."""
    suggestions = Translation.objects.filter(
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
    ).values("locale", "date")

    return group_dict_by(suggestions, "locale")


def query_entities(start_of_today):
    """Get entities created on the previous day."""
    return (
        Entity.objects.filter(
            date_created__gte=start_of_today - relativedelta(days=1),
            date_created__lt=start_of_today,
            obsolete=False,
            resource__project__disabled=False,
            resource__project__system_project=False,
            resource__project__visibility="public",
        )
        .distinct()
        .values(
            locale=F("resource__translatedresources__locale"),
            project=F("resource__project"),
        )
        .annotate(count=Count("*"))
    )


def count_entities(entities, project=None, locale=None):
    """Count the number of entities (i.e. source strings) with the given project and/or locale."""
    count = 0
    for ent in entities:
        if (project is None or project == ent["project"]) and (
            locale is None or locale == ent["locale"]
        ):
            count += ent["count"]
    return count


def get_locale_insights_snapshot(
    locale,
    start_of_today,
    privileged_users,
    contributors,
    active_users_actions,
    suggestions,
    activities,
    entities_count,
):
    """Create LocaleInsightsSnapshot instance for the given locale and day using given data."""
    all_managers, all_reviewers = get_privileged_users_data(privileged_users)
    all_contributors = {c["user"] for c in contributors}

    total_managers = len(all_managers)
    total_reviewers = len(all_reviewers)
    total_contributors = len(all_contributors)

    active_users_last_month = get_active_users_data(
        start_of_today,
        privileged_users,
        active_users_actions,
        all_reviewers,
        all_contributors,
        months=1,
    )
    active_users_last_3_months = get_active_users_data(
        start_of_today,
        privileged_users,
        active_users_actions,
        all_reviewers,
        all_contributors,
        months=3,
    )
    active_users_last_6_months = get_active_users_data(
        start_of_today,
        privileged_users,
        active_users_actions,
        all_reviewers,
        all_contributors,
        months=6,
    )
    active_users_last_12_months = get_active_users_data(
        start_of_today,
        privileged_users,
        active_users_actions,
        all_reviewers,
        all_contributors,
        months=12,
    )

    unreviewed_suggestions_lifespan = get_unreviewed_suggestions_lifespan_data(
        suggestions
    )

    time_to_review_suggestions = get_time_to_review_suggestions_data(
        activities, locale=locale.id
    )

    (
        human_translations,
        machinery_translations,
        new_suggestions,
        peer_approved,
        self_approved,
        rejected,
    ) = get_activity_charts_data(activities, locale=locale.id)

    return LocaleInsightsSnapshot(
        locale=locale,
        created_at=start_of_today,
        # AggregatedStats
        total_strings=locale.total_strings,
        approved_strings=locale.approved_strings,
        pretranslated_strings=locale.pretranslated_strings,
        strings_with_errors=locale.strings_with_errors,
        strings_with_warnings=locale.strings_with_warnings,
        unreviewed_strings=locale.unreviewed_strings,
        # Active users
        total_managers=total_managers,
        total_reviewers=total_reviewers,
        total_contributors=total_contributors,
        active_users_last_month=active_users_last_month,
        active_users_last_3_months=active_users_last_3_months,
        active_users_last_6_months=active_users_last_6_months,
        active_users_last_12_months=active_users_last_12_months,
        # Unreviewed suggestions lifespan
        unreviewed_suggestions_lifespan=unreviewed_suggestions_lifespan,
        # Time to review suggestions
        time_to_review_suggestions=time_to_review_suggestions,
        # Translation activity
        completion=round(locale.completed_percent, 2),
        human_translations=human_translations,
        machinery_translations=machinery_translations,
        new_source_strings=entities_count,
        # Review activity
        peer_approved=peer_approved,
        self_approved=self_approved,
        rejected=rejected,
        new_suggestions=new_suggestions,
    )


def get_project_locale_insights_snapshot(
    project_locale,
    start_of_today,
    activities,
    entities_count,
):
    """Create ProjectLocaleInsightsSnapshot instance for the given locale, project, and day using given data."""
    (
        human_translations,
        machinery_translations,
        new_suggestions,
        peer_approved,
        self_approved,
        rejected,
    ) = get_activity_charts_data(
        activities, locale=project_locale.project.id, project=project_locale.project.id
    )

    return ProjectLocaleInsightsSnapshot(
        project_locale=project_locale,
        created_at=start_of_today,
        # AggregatedStats
        total_strings=project_locale.total_strings,
        approved_strings=project_locale.approved_strings,
        pretranslated_strings=project_locale.pretranslated_strings,
        strings_with_errors=project_locale.strings_with_errors,
        strings_with_warnings=project_locale.strings_with_warnings,
        unreviewed_strings=project_locale.unreviewed_strings,
        # Translation activity
        completion=round(project_locale.completed_percent, 2),
        human_translations=human_translations,
        machinery_translations=machinery_translations,
        new_source_strings=entities_count,
        # Review activity
        peer_approved=peer_approved,
        self_approved=self_approved,
        rejected=rejected,
        new_suggestions=new_suggestions,
    )


def get_privileged_users_data(privileged_users):
    """Get all privileged users for the Active users panel."""
    all_managers = set()
    all_reviewers = set()

    for user in privileged_users:
        manager = user["managers_group__user"]
        translator = user["translators_group__user"]

        if manager:
            all_managers.add(manager)
            all_reviewers.add(manager)
        if translator:
            all_reviewers.add(translator)

    return all_managers, all_reviewers


def get_active_users_data(
    start_of_today,
    privileged_users,
    active_users_actions,
    all_reviewers,
    all_contributors,
    months=12,
):
    """Get active user counts for the Active users panel."""
    active_managers = set()
    active_reviewers = set()
    active_contributors = set()

    # Get active managers
    for user in privileged_users:
        manager = user["managers_group__user"]
        last_login = user["managers_group__user__last_login"]

        if last_login:
            if last_login + relativedelta(months=months) > start_of_today:
                active_managers.add(manager)

    # Get active reviewers and contributors. Make sure they are included among all
    # users, otherwise we might include PMs and privileged users of other locales.
    for action in active_users_actions:
        user = action["performed_by"]
        if user in all_reviewers and action["action_type"] in (
            "translation:approved",
            "translation:unapproved",
            "translation:rejected",
            "translation:unrejected",
        ):
            if action["created_at"] + relativedelta(months=months) > start_of_today:
                active_reviewers.add(user)

        if user in all_contributors and action["action_type"] == "translation:created":
            if action["created_at"] + relativedelta(months=months) > start_of_today:
                active_contributors.add(user)

    return {
        "managers": len(active_managers),
        "reviewers": len(active_reviewers),
        "contributors": len(active_contributors),
    }


def get_unreviewed_suggestions_lifespan_data(suggestions):
    """Get average age of the unreviewed suggestion."""
    unreviewed_suggestions_lifespan = timedelta()
    suggestion_count = len(suggestions)

    if suggestion_count > 0:
        total_suggestion_age = timedelta()

        for s in suggestions:
            total_suggestion_age += timezone.now() - s["date"]

        unreviewed_suggestions_lifespan = total_suggestion_age / suggestion_count

    return unreviewed_suggestions_lifespan


def get_time_to_review_suggestions_data(activities, locale):
    """Get average time to review a suggestion."""
    times_to_review = list()

    for (locale_, _), data in activities.items():
        if locale == locale_:
            times_to_review.extend(data["times_to_review"])

    if len(times_to_review) == 0:
        return timedelta()

    return sum(times_to_review, timedelta()) / len(times_to_review)


def query_activity_actions(start_of_today):
    """Get actions of the previous day, needed for the Translation and Review activity charts."""
    return ActionLog.objects.filter(
        created_at__gte=start_of_today - relativedelta(days=1),
        created_at__lt=start_of_today,
        translation__entity__resource__project__system_project=False,
        translation__entity__resource__project__visibility="public",
    ).values(
        "action_type",
        "performed_by",
        "translation",
        "translation__locale",
        machinery_sources=F("translation__machinery_sources"),
        user=F("translation__user"),
        approved_user=F("translation__approved_user"),
        date=F("translation__date"),
        approved_date=F("translation__approved_date"),
        rejected_date=F("translation__rejected_date"),
        project=F("translation__entity__resource__project"),
    )


def build_activity_charts_data(start_of_today, sync_user):
    """Fetch and prepare data for Translation activity and Review activity charts."""
    res = dict()

    for action in query_activity_actions(start_of_today):
        key = (action["translation__locale"], action["project"])
        if key not in res:
            res[key] = {
                "human_translations": set(),
                "machinery_translations": set(),
                "new_suggestions": set(),
                "peer_approved": set(),
                "self_approved": set(),
                "rejected": set(),
                "times_to_review": list(),
            }
        data = res[key]

        action_type = action["action_type"]
        performed_by = action["performed_by"]
        translation = action["translation"]

        # Review actions performed by the sync process are ignored, because they
        # aren't explicit user review actions.
        performed_by_sync = performed_by == sync_user

        if action_type == "translation:created":
            if len(action["machinery_sources"]) == 0:
                data["human_translations"].add(translation)
            else:
                data["machinery_translations"].add(translation)

            if not action["approved_date"] or action["approved_date"] > action["date"]:
                data["new_suggestions"].add(translation)

            # Self-approval can also happen on translation submission
            if performed_by == action["approved_user"] and not performed_by_sync:
                data["self_approved"].add(translation)

        elif action_type == "translation:approved" and not performed_by_sync:
            if performed_by == action["user"]:
                data["self_approved"].add(translation)
            else:
                data["peer_approved"].add(translation)
                if action["approved_date"]:
                    data["times_to_review"].append(
                        action["approved_date"] - action["date"]
                    )

        elif action_type == "translation:rejected" and not performed_by_sync:
            data["rejected"].add(translation)
            if action["rejected_date"]:
                data["times_to_review"].append(action["rejected_date"] - action["date"])

    return res


def get_activity_charts_data(activities, project=None, locale=None):
    """Get data for Translation activity and Review activity charts."""
    human_translations = set()
    machinery_translations = set()
    new_suggestions = set()
    peer_approved = set()
    self_approved = set()
    rejected = set()

    for (locale_, project_), data in activities.items():
        if (project is None or project == project_) and (
            locale is None or locale == locale_
        ):
            human_translations.update(data["human_translations"])
            machinery_translations.update(data["machinery_translations"])
            new_suggestions.update(data["new_suggestions"])
            peer_approved.update(data["peer_approved"])
            self_approved.update(data["self_approved"])
            rejected.update(data["rejected"])

    return (
        len(human_translations),
        len(machinery_translations),
        len(new_suggestions),
        len(peer_approved),
        len(self_approved),
        len(rejected),
    )
