import logging

from celery import shared_task
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import F
from django.contrib.auth.models import User
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Entity, Locale, Project, ProjectLocale, Translation
from pontoon.base.utils import group_dict_by
from pontoon.insights.models import (
    LocaleInsightsSnapshot,
    ProjectInsightsSnapshot,
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

    actions = get_activity_actions(start_of_today)
    entities = get_entities(start_of_today)
    sync_user = User.objects.get(email="pontoon-sync@example.com").pk
    log.info(f"Collect insights for {date}: Common data gathered.")

    collect_project_insights(start_of_today, actions, entities, sync_user)
    log.info(f"Collect insights for {date}: Project insights created.")

    collect_project_locale_insights(start_of_today)
    log.info(f"Collect insights for {date}: ProjectLocale insights created.")

    collect_locale_insights(start_of_today, actions, entities, sync_user)
    log.info(f"Collect insights for {date}: Locale insights created.")


def collect_project_insights(start_of_today, actions, entities, sync_user):
    """
    Collect insights for each available Project.
    """
    # Get data sources to retrieve insights from
    actions_dict = group_dict_by(actions, "translation__entity__resource__project")
    entities_dict = group_dict_by(entities, "resource__project")

    ProjectInsightsSnapshot.objects.bulk_create(
        [
            get_project_insights_snapshot(
                project,
                start_of_today,
                actions_dict[project.id],
                entities_dict[project.id],
                sync_user,
            )
            for project in Project.objects.available()
        ],
        batch_size=1000,
    )


def collect_project_locale_insights(start_of_today):
    """
    Collect insights for each available ProjectLocale.
    """
    ProjectLocaleInsightsSnapshot.objects.bulk_create(
        [
            ProjectLocaleInsightsSnapshot(
                project_locale=project_locale,
                created_at=start_of_today,
                completion=round(project_locale.completed_percent, 2),
                # AggregatedStats
                total_strings=project_locale.total_strings,
                approved_strings=project_locale.approved_strings,
                fuzzy_strings=project_locale.fuzzy_strings,
                strings_with_errors=project_locale.strings_with_errors,
                strings_with_warnings=project_locale.strings_with_warnings,
                unreviewed_strings=project_locale.unreviewed_strings,
            )
            for project_locale in ProjectLocale.objects.all()
        ],
        batch_size=1000,
    )


def collect_locale_insights(start_of_today, actions, entities, sync_user):
    """
    Collect insights for each available Locale.
    """
    # Get data sources to retrieve insights from
    privileged_users = get_privileged_users()
    contributors = get_contributors()
    active_users_actions = get_active_users_actions(start_of_today)
    suggestions = get_suggestions()

    actions_dict = group_dict_by(actions, "translation__locale")
    entities_dict = group_dict_by(entities, "resource__translatedresources__locale")

    LocaleInsightsSnapshot.objects.bulk_create(
        [
            get_locale_insights_snapshot(
                locale,
                start_of_today,
                privileged_users[locale.id],
                contributors[locale.id],
                active_users_actions[locale.id],
                suggestions[locale.id],
                actions_dict[locale.id],
                entities_dict[locale.id],
                sync_user,
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
    system_users = User.objects.filter(
        email__regex=r"^pontoon-(\w+)@example.com$",
    ).values("pk")

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
        fuzzy=False,
        rejected=False,
        entity__obsolete=False,
        entity__resource__project__disabled=False,
        entity__resource__project__system_project=False,
        entity__resource__project__visibility="public",
    ).values("locale", "date")

    return group_dict_by(suggestions, "locale")


def get_activity_actions(start_of_today):
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
        "translation__entity__resource__project",
        "translation__machinery_sources",
        "translation__user",
        "translation__approved_user",
        "translation__date",
        "translation__approved_date",
    )


def get_entities(start_of_today):
    """Get entities created on the previous day."""
    return Entity.objects.filter(
        date_created__gte=start_of_today - relativedelta(days=1),
        date_created__lt=start_of_today,
        obsolete=False,
        resource__project__disabled=False,
        resource__project__system_project=False,
        resource__project__visibility="public",
    ).values("pk", "resource__translatedresources__locale", "resource__project")


def get_locale_insights_snapshot(
    locale,
    start_of_today,
    privileged_users,
    contributors,
    active_users_actions,
    suggestions,
    activity_actions,
    entities,
    sync_user,
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

    (
        human_translations,
        machinery_translations,
        new_suggestions,
        peer_approved,
        self_approved,
        rejected,
    ) = get_activity_charts_data(activity_actions, sync_user)

    return LocaleInsightsSnapshot(
        locale=locale,
        created_at=start_of_today,
        # AggregatedStats
        total_strings=locale.total_strings,
        approved_strings=locale.approved_strings,
        fuzzy_strings=locale.fuzzy_strings,
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
        # Translation activity
        completion=round(locale.completed_percent, 2),
        human_translations=len(human_translations),
        machinery_translations=len(machinery_translations),
        new_source_strings=len(entities),
        # Review activity
        peer_approved=len(peer_approved),
        self_approved=len(self_approved),
        rejected=len(rejected),
        new_suggestions=len(new_suggestions),
    )


def get_project_insights_snapshot(
    project, start_of_today, activity_actions, entities, sync_user,
):
    """Create ProjectInsightsSnapshot instance for the given project and day using given data."""
    (
        human_translations,
        machinery_translations,
        new_suggestions,
        peer_approved,
        self_approved,
        rejected,
    ) = get_activity_charts_data(activity_actions, sync_user)

    return ProjectInsightsSnapshot(
        project=project,
        created_at=start_of_today,
        # AggregatedStats
        total_strings=project.total_strings,
        approved_strings=project.approved_strings,
        fuzzy_strings=project.fuzzy_strings,
        strings_with_errors=project.strings_with_errors,
        strings_with_warnings=project.strings_with_warnings,
        unreviewed_strings=project.unreviewed_strings,
        # Translation activity
        completion=round(project.completed_percent, 2),
        human_translations=len(human_translations),
        machinery_translations=len(machinery_translations),
        new_source_strings=len(entities),
        # Review activity
        peer_approved=len(peer_approved),
        self_approved=len(self_approved),
        rejected=len(rejected),
        new_suggestions=len(new_suggestions),
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


def get_activity_charts_data(activity_actions, sync_user):
    """Get data for Translation activity and Review activity charts."""
    human_translations = set()
    machinery_translations = set()
    new_suggestions = set()
    peer_approved = set()
    self_approved = set()
    rejected = set()

    for action in activity_actions:
        action_type = action["action_type"]
        performed_by = action["performed_by"]
        translation = action["translation"]
        machinery_sources = action["translation__machinery_sources"]
        user = action["translation__user"]
        approved_user = action["translation__approved_user"]
        date = action["translation__date"]
        approved_date = action["translation__approved_date"]

        # Review actions performed by the sync process are ignored, because they
        # aren't explicit user review actions.
        performed_by_sync = performed_by == sync_user

        if action_type == "translation:created":
            if len(machinery_sources) == 0:
                human_translations.add(translation)
            else:
                machinery_translations.add(translation)

            if not approved_date or approved_date > date:
                new_suggestions.add(translation)

            # Self-approval can also happen on translation submission
            if performed_by == approved_user and not performed_by_sync:
                self_approved.add(translation)

        elif action_type == "translation:approved" and not performed_by_sync:
            if performed_by == user:
                self_approved.add(translation)
            else:
                peer_approved.add(translation)

        elif action_type == "translation:rejected" and not performed_by_sync:
            rejected.add(translation)

    return (
        human_translations,
        machinery_translations,
        new_suggestions,
        peer_approved,
        self_approved,
        rejected,
    )
